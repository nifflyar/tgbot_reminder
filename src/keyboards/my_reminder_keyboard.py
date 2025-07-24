from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


from lexicon.lexicon_keyboards import lexicon_kb




async def my_reminders(lang : str, len : int, page : int, active_archive: str, type : str, has_reminder : bool = True):
    kb = InlineKeyboardBuilder()

    if type in ["onetime"]:
        kb.row(InlineKeyboardButton(text=f"[{lexicon_kb[lang]['onetime_type']}]", callback_data="my_onetime"),
               InlineKeyboardButton(text=lexicon_kb[lang]['regular_type'], callback_data="my_regular"))
    else:
        kb.row(InlineKeyboardButton(text=f"{lexicon_kb[lang]['onetime_type']}", callback_data="my_onetime"),
               InlineKeyboardButton(text=f"[{lexicon_kb[lang]['regular_type']}]", callback_data="my_regular"))
        
    if type != "onetime":
        if type == "hourly":
            kb.row(
                InlineKeyboardButton(text=f"[{lexicon_kb[lang]['hourly_type']}]", callback_data="my_hourly"),
                InlineKeyboardButton(text=f"{lexicon_kb[lang]['daily_type']}", callback_data="my_daily"),
                InlineKeyboardButton(text=f"{lexicon_kb[lang]['yearly_type']}", callback_data="my_yearly"))
        if type == "daily":
            kb.row(
                InlineKeyboardButton(text=f"{lexicon_kb[lang]['hourly_type']}", callback_data="my_hourly"),
                InlineKeyboardButton(text=f"[{lexicon_kb[lang]['daily_type']}]", callback_data="my_daily"),
                InlineKeyboardButton(text=f"{lexicon_kb[lang]['yearly_type']}", callback_data="my_yearly"))
            
        if type == "yearly":
            kb.row(
                InlineKeyboardButton(text=f"{lexicon_kb[lang]['hourly_type']}", callback_data="my_hourly"),
                InlineKeyboardButton(text=f"{lexicon_kb[lang]['daily_type']}", callback_data="my_daily"),
                InlineKeyboardButton(text=f"[{lexicon_kb[lang]['yearly_type']}]", callback_data="my_yearly"))
        
        

   

    if ( (page == 0 and len == 0) or (page == 1 and len == 1)):
        kb.row(InlineKeyboardButton(text=lexicon_kb['arrows']['empty'], callback_data='empty'),
               InlineKeyboardButton(text=f"{page}/{len}", callback_data='empty'),
               InlineKeyboardButton(text=lexicon_kb['arrows']['empty'], callback_data='empty'))
    

    elif (page == 1):
        kb.row(InlineKeyboardButton(text=lexicon_kb['arrows']['empty'], callback_data='empty'),
               InlineKeyboardButton(text=f"{page}/{len}", callback_data='empty'),
               InlineKeyboardButton(text=lexicon_kb['arrows']['right'], callback_data=f"nextpage_{page}_{type}_{active_archive}"))
    
    elif (page != len):
        kb.row(InlineKeyboardButton(text=lexicon_kb['arrows']['left'], callback_data=f"previouspage_{page}_{type}_{active_archive}"),
               InlineKeyboardButton(text=f"{page}/{len}", callback_data='empty'),
               InlineKeyboardButton(text=lexicon_kb['arrows']['right'], callback_data=f"nextpage_{page}_{type}_{active_archive}"))
    
    elif (page == len):
        kb.row(InlineKeyboardButton(text=lexicon_kb['arrows']['left'], callback_data=f"previouspage_{page}_{type}_{active_archive}"),
               InlineKeyboardButton(text=f"{page}/{len}", callback_data='empty'),
               InlineKeyboardButton(text=lexicon_kb['arrows']['empty'], callback_data='empty'))
        

    


   

    if active_archive == "active":
        if has_reminder:
            kb.row(InlineKeyboardButton(text=lexicon_kb[lang]["edit"], callback_data=f"edit_1_{type}_{active_archive}"),
                   InlineKeyboardButton(text = lexicon_kb[lang]["archive"], callback_data=f'archive_{type}_{active_archive}'))
        else:
            kb.row(InlineKeyboardButton(text = lexicon_kb[lang]["archive"], callback_data=f'archive_{type}_{active_archive}'))

    elif active_archive == "archive":
        if has_reminder:
            kb.row(InlineKeyboardButton(text=lexicon_kb[lang]["edit"], callback_data=f"edit_1_{type}_{active_archive}"),
                   InlineKeyboardButton(text = lexicon_kb[lang]["active"], callback_data=f'active_{type}_{active_archive}'))
        else:
            kb.row(InlineKeyboardButton(text = lexicon_kb[lang]["active"], callback_data=f'active_{type}_{active_archive}'))


    kb.row(InlineKeyboardButton(text = lexicon_kb[lang]["back_to_main"], callback_data='back_main'))

    return kb.as_markup()


async def edit_reminder(lang : str, quantity : int, len : int, page : int, active_archive: str, type : str):
    kb = InlineKeyboardBuilder()
    

    start = 5 * (page-1)
    end = 5 * page if (5 * page) < quantity else quantity


    for i in range(start, end):
        kb.add(InlineKeyboardButton(text = f"{i+1}", callback_data=f'edit-remind_{i}_{type}_{active_archive}_{page}'))
    kb.adjust(5)


    if ( (page == 0 and len == 0) or (page == 1 and len == 1)):
        kb.row(InlineKeyboardButton(text=lexicon_kb['arrows']['empty'], callback_data='empty'),
               InlineKeyboardButton(text=f"{page}/{len}", callback_data='empty'),
               InlineKeyboardButton(text=lexicon_kb['arrows']['empty'], callback_data='empty'))
    

    elif (page == 1):
        kb.row(InlineKeyboardButton(text=lexicon_kb['arrows']['empty'], callback_data='empty'),
               InlineKeyboardButton(text=f"{page}/{len}", callback_data='empty'),
               InlineKeyboardButton(text=lexicon_kb['arrows']['right'], callback_data=f"editnextpage_{page}_{type}_{active_archive}"))
    
    elif (page != len):
        kb.row(InlineKeyboardButton(text=lexicon_kb['arrows']['left'], callback_data=f"editpreviouspage_{page}_{type}_{active_archive}"),
               InlineKeyboardButton(text=f"{page}/{len}", callback_data='empty'),
               InlineKeyboardButton(text=lexicon_kb['arrows']['right'], callback_data=f"editnextpage__{page}_{type}_{active_archive}"))
    
    elif (page == len):
        kb.row(InlineKeyboardButton(text=lexicon_kb['arrows']['left'], callback_data=f"editpreviouspage_{page}_{type}_{active_archive}"),
               InlineKeyboardButton(text=f"{page}/{len}", callback_data='empty'),
               InlineKeyboardButton(text=lexicon_kb['arrows']['empty'], callback_data='empty'))


    kb.row(InlineKeyboardButton(text = lexicon_kb[lang]["get_back"], callback_data=f'{active_archive}_{type}_{active_archive}'))
    
    return kb.as_markup()





async def editing_reminder(lang : str, active_archive : str, page : int, type : str, number : int):

    kb = InlineKeyboardBuilder()

    if active_archive == "active" or type in ["hourly", "daily"]:

        if active_archive == "active" and type in ["hourly", "daily", "yearly"]:
            kb.row(InlineKeyboardButton(text = lexicon_kb[lang]['edit_text'], callback_data=f'editreminder_{number}_{page}_{type}_{active_archive}'),
                   InlineKeyboardButton(text = lexicon_kb[lang]['deactivate_text'], callback_data=f'deactivatereminder_{number}_{page}_{type}_{active_archive}'),
                   InlineKeyboardButton(text = lexicon_kb[lang]['delete_text'], callback_data=f'deletereminder_{number}_{page}_{type}_{active_archive}'))

        elif active_archive == "archive" and type in ["hourly", "daily", "yearly"]:
            kb.row(InlineKeyboardButton(text = lexicon_kb[lang]['edit_text'], callback_data=f'editreminder_{number}_{page}_{type}_{active_archive}'),
                   InlineKeyboardButton(text = lexicon_kb[lang]["activate_text"], callback_data=f'activatereminder_{number}_{page}_{type}_{active_archive}'),
                   InlineKeyboardButton(text = lexicon_kb[lang]['delete_text'], callback_data=f'deletereminder_{number}_{page}_{type}_{active_archive}'))
        
        elif type == "onetime":
            kb.row(InlineKeyboardButton(text = lexicon_kb[lang]['edit_text'], callback_data=f'editreminder_{number}_{page}_{type}_{active_archive}'),
                   InlineKeyboardButton(text = lexicon_kb[lang]['delete_text'], callback_data=f'deletereminder_{number}_{page}_{type}_{active_archive}'))

    else:
        kb.row(InlineKeyboardButton(text = lexicon_kb[lang]['delete_text'], callback_data=f'deletereminder_{number}_{page}_{type}_{active_archive}'))

    kb.row(InlineKeyboardButton(text = lexicon_kb[lang]['cancel'], callback_data=f'edit_{page}_{type}_{active_archive}')) 
    return kb.as_markup()


async def deactivate_reminder(lang : str, active_archive : str, page : int, type : str, number : int):

    kb = InlineKeyboardBuilder()

    kb.row(InlineKeyboardButton(text = lexicon_kb[lang]["no"], callback_data=f'edit-remind_{number}_{type}_{active_archive}_{page}'),
            InlineKeyboardButton(text = lexicon_kb[lang]["yes"], callback_data=f'confirmdeactivatereminder_{number}_{page}_{type}_{active_archive}'))

    return kb.as_markup()


async def activate_reminder(lang : str, active_archive : str, page : int, type : str, number : int):

    kb = InlineKeyboardBuilder()

    kb.row(InlineKeyboardButton(text = lexicon_kb[lang]["no"], callback_data=f'edit-remind_{number}_{type}_{active_archive}_{page}'),
            InlineKeyboardButton(text = lexicon_kb[lang]["yes"], callback_data=f'confirmactivatereminder_{number}_{page}_{type}_{active_archive}'))

    return kb.as_markup()


async def delete_reminder(lang : str, active_archive : str, page : int, type : str, number : int):
    kb = InlineKeyboardBuilder()

    kb.row(InlineKeyboardButton(text = lexicon_kb[lang]["no"], callback_data=f'edit-remind_{number}_{type}_{active_archive}_{page}'),
            InlineKeyboardButton(text = lexicon_kb[lang]["yes"], callback_data=f'confirmdeletereminder_{number}_{page}_{type}_{active_archive}'))

    return kb.as_markup()



async def edit_info_reminder(lang : str, active_archive : str, page : int, type : str, number : int):
    kb = InlineKeyboardBuilder()


    if type == "onetime":
        kb.row(InlineKeyboardButton(text = f"{lexicon_kb[lang]['title']}", callback_data=f'my_edit_name_{number}_{page}_{type}_{active_archive}'),
                InlineKeyboardButton(text = f"{lexicon_kb[lang]['date']}", callback_data=f'my_edit_date_{number}_{page}_{type}_{active_archive}'),
                InlineKeyboardButton(text=f"{lexicon_kb[lang]['time']}", callback_data=f'my_edit_time_{number}_{page}_{type}_{active_archive}'))
        
                
        
    elif type == "hourly":
        kb.row(InlineKeyboardButton(text = f"{lexicon_kb[lang]['title']}", callback_data=f'my_edit_name_{number}_{page}_{type}_{active_archive}'),
                InlineKeyboardButton(text=f"{lexicon_kb[lang]['interval']}", callback_data=f'my_edit_interval_{number}_{page}_{type}_{active_archive}'),
                InlineKeyboardButton(text=f"{lexicon_kb[lang]['start_time']}", callback_data=f'my_edit_starttime_{number}_{page}_{type}_{active_archive}'),
                InlineKeyboardButton(text=f"{lexicon_kb[lang]['end_time']}", callback_data=f'my_edit_endtime_{number}_{page}_{type}_{active_archive}'))
        
        

    elif type == "daily":
        kb.row(InlineKeyboardButton(text = f"{lexicon_kb[lang]['title']}", callback_data=f'my_edit_name_{number}_{page}_{type}_{active_archive}'),
                InlineKeyboardButton(text=f"{lexicon_kb[lang]['time']}", callback_data=f'my_edit_time_{number}_{page}_{type}_{active_archive}'))
        
    elif type == "yearly":
        kb.row(InlineKeyboardButton(text = f"{lexicon_kb[lang]['title']}", callback_data=f'my_edit_name_{number}_{page}_{type}_{active_archive}'),
                InlineKeyboardButton(text=f"{lexicon_kb[lang]['date']}", callback_data=f'my_edit_yearlydate_{number}_{page}_{type}_{active_archive}'))


    kb.row(InlineKeyboardButton(text=f"{lexicon_kb[lang]['cancel']}", callback_data=f"edit-remind_{number}_{type}_{active_archive}_{page}"),
                InlineKeyboardButton(text = f"{lexicon_kb[lang]['save']}", callback_data=f'my_new_save_{number}_{page}_{type}_{active_archive}'))
                
    
    return kb.as_markup()




async def editing_info(lang : str, active_archive : str, page : int, type : str, number : int):
    kb = InlineKeyboardBuilder()

    kb.row(InlineKeyboardButton(text = f"{lexicon_kb[lang]['cancel']}", callback_data=f'edit-remind_{number}_{type}_{active_archive}_{page}'),
        InlineKeyboardButton(text = f"{lexicon_kb[lang]['dont_change']}", callback_data=f'my_dont_change_{number}_{type}_{active_archive}_{page}'))
    
    return kb.as_markup()