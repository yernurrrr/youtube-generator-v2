import streamlit as st
import os
from google import genai
from google.genai.errors import APIError

# --- КОНФИГУРАЦИЯ API И МОДЕЛИ ---
# Ключ GEMINI_API_KEY будет получен из Streamlit Secrets
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.5-flash"
FREE_LIMIT = 5 # Константа для лимита бесплатных запросов

# !!! КОНФИГУРАЦИЯ МОНЕТИЗАЦИИ !!!
PREMIUM_KEY = "TurboTitle2025" # <--- ОБНОВИТЕ ЭТОТ КЛЮЧ! (Выдавать подписчикам)
BOOSTY_LINK = "https://boosty.to/youtube_titles_ai" # <--- ОБНОВИТЕ ЭТУ ССЫЛКУ!

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

# 1. Поле для ввода ключа в сайдбаре
user_key = st.sidebar.text_input(
    "🔑 Введите Премиум-Ключ для безлимита:",
    key="premium_key",
    placeholder="Код, выданный на Boosty"
)
is_premium = user_key == PREMIUM_KEY

# --- ИНИЦИАЛИЗАЦИЯ СЧЕТЧИКА В СЕССИИ ---
if 'count' not in st.session_state:
    st.session_state.count = 0

# --- ВЫВОД СТАТУСА ---
st.markdown("---")
if is_premium:
    st.markdown("⚡️ **Ваш статус:** Премиум. 🎉 **Запросы:** Безлимитно!")
else:
    st.markdown(f"**Ваш статус:** Бесплатный. 🔑 **Осталось запросов:** {FREE_LIMIT - st.session_state.count}")

st.markdown(
    f"**⚡️ Нужны безлимитные запросы?** [Подпишитесь здесь!]({BOOSTY_LINK})"
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

# 3. Пустой контейнер для результатов.
results_placeholder = st.empty()

if st.button("Сгенерировать 🚀"):

    # --- ЛОГИКА ПРОВЕРКИ ЛИМИТА (ИЗМЕНЕНО) ---
    # Лимит проверяется ТОЛЬКО если пользователь НЕ премиум
    if not is_premium and st.session_state.count >= FREE_LIMIT:
        results_placeholder.error(
            "🛑 **Лимит запросов исчерпан.** Вы израсходовали 5 бесплатных генераций. "
            f"Пожалуйста, оформите подписку для продолжения работы по ссылке: [Подписаться]({BOOSTY_LINK})"
        )
    elif not text_input:
        results_placeholder.warning("Пожалуйста, введите текст для генерации заголовка")
    else:
        # Если лимит не исчерпан ИЛИ пользователь премиум, выполняем генерацию
        with st.spinner("Генерация... Это может занять несколько секунд."):

            # Вызов функции генерации
            result_text = generate_titles(text_input, style_selection)

            # *** ОТОБРАЖЕНИЕ РЕЗУЛЬТАТА В КОНТЕЙНЕРЕ ***
            with results_placeholder.container():
                st.success("✅ Готово! Ваши заголовки:")
                st.markdown(result_text)

            # *** УВЕЛИЧЕНИЕ СЧЕТЧИКА ТОЛЬКО ДЛЯ БЕСПЛАТНЫХ ПОЛЬЗОВАТЕЛЕЙ ***
            if not is_premium:
                st.session_state.count += 1

            # *** ПЕРЕЗАПУСК ПРИЛОЖЕНИЯ ДЛЯ НЕМЕДЛЕННОГО ОБНОВЛЕНИЯ UI ***
            st.rerun()
