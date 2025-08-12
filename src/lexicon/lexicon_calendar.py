from src.keyboards.aiogram_calendar.schemas import CalendarLabels



lexicon_calendar = {

    "ru" : {
        "days_of_week" :["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
        "months" : ["Янв", "Февр", "Март", "Апр", "Май", "Июнь", "Июль", "Авг", "Сент", "Окт", "Нояб", "Дек"],
        "cancel" : "Отмена",
        "do_not_change" : "Не изменять",
        "today" : "Сегодня",
        "tomorrow" : "Завтра"
    },

    "en" : {
        "days_of_week" : ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
        "months" : [ "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        "cancel" : "Cancel",
        "do_not_change" : "Don't change",
        "today" : "Today",
        "tomorrow" : "Tomorrow"
    },

    "kk":{
        "days_of_week" : ["Дс", "Сс", "Ср", "Бс", "Жм", "Сн", "Жк"],
        "months" : ["Қаң", "Ақп", "Нау", "Сәу", "Мам", "Мау", "Шіл", "Там", "Қыр", "Қаз", "Қар", "Жел"],
        "cancel" : "Бас тарту",
        "do_not_change" : "Өзгертпеу",
        "today" : "Бүгін",
        "tomorrow" : "Ертең"
    },
    
}

lexicon_clndr = {
    "ru" : "ru_RU",
    "en" : "en_US",
    "kk" : "kk_KZ",
} 



lexicon_locale = {

    "ru": CalendarLabels(
        days_of_week=["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
        months=["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"],
        cancel_caption="",
        today_caption="Сегодня",
        tomorrow_caption="Завтра"
    ),

    "kk": CalendarLabels(
        days_of_week=["Дс", "Сс", "Ср", "Бс", "Жм", "Сн", "Жк"],
        months=["Қаң", "Ақп", "Нау", "Сәу", "Мам", "Мау", "Шіл", "Там", "Қыр", "Қаз", "Қар", "Жел"],
        cancel_caption="",
        today_caption="Бүгін",
        tomorrow_caption="Ертең"
    ),

    "en": CalendarLabels(today_caption="Today",
                         tomorrow_caption="Tomorrow",
                         cancel_caption="")
}