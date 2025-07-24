from src.keyboards.aiogram_calendar.schemas import CalendarLabels



lexicon_calendar = {

    "ru" : {
        "days_of_week" :["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
        "months" : ["Янв", "Февр", "Март", "Апр", "Май", "Июнь", "Июль", "Авг", "Сент", "Окт", "Нояб", "Дек"],
        "cancel" : "отмена",
        "do_not_change" : "не изменять",
        "today" : "сегодня",
        "tomorrow" : "завтра"
    },

    "en" : {
        "days_of_week" : ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
        "months" : [ "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        "cancel" : "cancel",
        "do_not_change" : "do not change",
        "today" : "today",
        "tomorrow" : "tomorrow"
    }
    
}

lexicon_clndr = {
    "ru" : "ru_RU",
    "en" : "en_US",
} 



lexicon_locale = {

    "ru": CalendarLabels(
        days_of_week=["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
        months=["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"],
        cancel_caption="",
        today_caption="сегодня",
        tomorrow_caption="завтра"
    ),
    # "kk": CalendarLabels(
    #     days_of_week=["Дс", "Сс", "Ср", "Бс", "Жм", "Сн", "Жк"],
    #     months=["Қаң", "Ақп", "Нау", "Сәу", "Мам", "Мау", "Шіл", "Там", "Қыр", "Қаз", "Қар", "Жел"],
    #     cancel_caption="Бас тарту",
    #     today_caption="Бүгін"
    # ),
    "en": CalendarLabels(today_caption="today",
                         tomorrow_caption="tomorrow",
                         cancel_caption="")
}