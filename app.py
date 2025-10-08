import streamlit as st
import os
from google import genai
from google.genai.errors import APIError

# --- КОНФИГУРАЦИЯ API И МОДЕЛИ ---
# Ключ GEMINI_API_KEY будет получен из Streamlit Secrets (или из локального окружения)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.5-flash"
FREE_LIMIT = 5 # Константа для лимита бесплатных запросов

def generate_titles(prompt_text, style):
    """Отправляет запрос к модели Gemini, включая выбранный стиль."""
    if not GEMINI_API_KEY:
        return "Ошибка: Не найден GEMINI_API_KEY. Пожалуйста, установите переменную окружения (на Streamlit Cloud)."

    client = genai.Client(api_key=GEMINI_API_KEY)

    # Инструкции (системный промпт), которые делают модель "экспертом"
    system_instruction = (
        f"Ты эксперт по созданию привлекательных и кликабельных заголовков для YouTube-видео. Твой стиль должен быть: '{style}'. "
        "Отвечай только списком из 5 уникальных вариантов, не добавляя лишнего текста или комментариев."
    )

    full_prompt = (
        f"Сгенерируй 5 вариантов заголовков для YouTube-видео на основе следующей темы: '{prompt_text}'"
    )

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=full_prompt,
            config={"system_instruction": system_instruction}
        )
        return response.text
    except APIError as e:
        return f"Произошла ошибка API: {e}"
    except Exception as e:
        return f"Произошла непредвиденная ошибка: {e}"

# --- ОСНОВНАЯ ЛОГИКА STREAMLIT ---

st.set_page_config(page_title="Генератор Заголовков", layout="centered")
st.title("🔥 Генератор заголовков для YouTube (MVP)")

# --- ИНИЦИАЛИЗАЦИЯ СЧЕТЧИКА В СЕССИИ ---
if 'count' not in st.session_state:
    st.session_state.count = 0

# Вывод текущего статуса и ссылки на монетизацию (обновляется при каждом новом запросе)
st.markdown(f"**Ваш статус:** Бесплатный. 🔑 **Осталось запросов:** {FREE_LIMIT - st.session_state.count}")
st.markdown("---")
st.markdown(
    "**⚡️ Нужны безлимитные запросы?** [Подпишитесь здесь! (Ваша ссылка на Boosty/Patreon)](ВАША_ССЫЛКА_ДЛЯ_ОПЛАТЫ)"
)
st.markdown("---")

# 1. Поле ввода темы
text_input = st.text_input("Введите тему вашего видео:", placeholder="Как быстро выучить Python", key="topic")

# 2. Поле выбора стиля
style_selection = st.selectbox(
    "Выберите желаемый стиль заголовков:",
    options=["Информационный", "Кликбейтный (интригующий)", "Юмористический", "Серьезный"],
    key="style"
)

# 3. Пустой контейнер для результатов. Это предотвратит дублирование результатов.
results_placeholder = st.empty()

if st.button("Сгенерировать 🚀"):

    # --- ЛОГИКА ПРОВЕРКИ ЛИМИТА ---
    if st.session_state.count >= FREE_LIMIT:
        results_placeholder.error(
            "🛑 **Лимит запросов исчерпан.** Вы израсходовали 5 бесплатных генераций. "
            "Пожалуйста, оформите подписку для продолжения работы."
        )
    elif not text_input:
        results_placeholder.warning("Пожалуйста, введите текст для генерации заголовка")
    else:
        # Если лимит не исчерпан, выполняем генерацию
        with st.spinner("Генерация... Это может занять несколько секунд."):

            # Вызов функции генерации
            result_text = generate_titles(text_input, style_selection)

            # *** ОТОБРАЖЕНИЕ РЕЗУЛЬТАТА В КОНТЕЙНЕРЕ ***
            with results_placeholder.container():
                st.success("✅ Готово! Ваши заголовки:")
                st.markdown(result_text)

            # *** УВЕЛИЧЕНИЕ СЧЕТЧИКА ПОСЛЕ УСПЕШНОЙ ГЕНЕРАЦИИ ***
            st.session_state.count += 1
            # Здесь НЕТ st.rerun(), чтобы сохранить заголовки на экране.
            # Счетчик обновится при следующей генерации.
