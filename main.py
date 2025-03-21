from logic import DB_Manager
from config import *
from telebot import TeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telebot import types

bot = TeleBot(TOKEN)
hideBoard = types.ReplyKeyboardRemove() 

cancel_button = "Отмена 🚫"
def canсel(message):
    bot.send_message(message.chat.id, "Чтобы посмотреть команды, используй - /info", reply_markup=types.ReplyKeyboardRemove())
  
def no_projects(message):
    bot.send_message(message.chat.id, 'У тебя пока нет проектов!\nМожешь добавить их с помошью команды /new_project')

def gen_inline_markup(rows):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    for row in rows:
        markup.add(InlineKeyboardButton(row, callback_data=row))
    return markup

def gen_markup(rows):
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.row_width = 1
    for row in rows:
        markup.add(KeyboardButton(row))
    markup.add(KeyboardButton(cancel_button))
    return markup


attributes_of_projects = {'Имя проекта' : ["Введите новое имя проекта", "project_name"],
                          "Описание" : ["Введите новое описание проекта", "description"],
                          "Ссылка" : ["Введите новую ссылку на проект", "url"],
                          "Статус" : ["Выберите новый статус задачи", "status_id"]}

def info_project(message, user_id, project_name):
    info = manager.get_project_info(user_id, project_name)[0]
    skills = manager.get_project_skills(project_name)
    if not skills:
        skills = 'Навыки пока не добавлены'
    bot.send_message(message.chat.id, f"""Project name: {info[0]}
Description: {info[1]}
Link: {info[2]}
Status: {info[3]}
Skills: {skills}
""")

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, """Привет! Я бот-менеджер проектов
Помогу тебе сохранить твои проекты и информацию о них!) 
""")
    info(message)
    
@bot.message_handler(commands=['info'])
def info(message):
    bot.send_message(message.chat.id,
"""
Вот команды которые могут тебе помочь:

/new_project - используй для добавления нового проекта
/skills - используй для добавления новых навыков
/projects - используй для просмотра информации о проекте
/delete - используй для удаления проекта
/update_projects - используй для изменения проекта
/update_status - изменить статус
/delete_status - удалить статус
/delete_project_skill - удалить навык из проекта
/update_project_skill - изменить навык в проекте

Также ты можешь ввести имя проекта и узнать информацию о нем!""")
    

@bot.message_handler(commands=['new_project'])
def addtask_command(message):
    bot.send_message(message.chat.id, "Как ты назовешь проект?🧐")
    bot.register_next_step_handler(message, name_project) 

def name_project(message):
    name = message.text
    user_id = message.from_user.id
    data = [user_id, name]
    bot.send_message(message.chat.id, "Введите свою ссылку на проект:")
    bot.register_next_step_handler(message, link_project, data=data)

def link_project(message, data):
    data.append(message.text) 
    bot.send_message(message.chat.id, "Введите описание проекта:")
    bot.register_next_step_handler(message, status_project, data=data)

def status_project(message, data):
    data.append(message.text)
    statuses = [x[0] for x in manager.get_statuses()] 
    bot.send_message(message.chat.id, "Введите текущий статус проекта", reply_markup=gen_markup(statuses))
    bot.register_next_step_handler(message, callback_project, data=data, statuses=statuses)


def callback_project(message, data, statuses):
    status = message.text
    if message.text == cancel_button:
        canсel(message)
        return
    if status not in statuses:
        bot.send_message(message.chat.id, "Ты выбрал статус не из списка, попробуй еще раз!🫢", reply_markup=gen_markup(statuses))
        bot.register_next_step_handler(message, callback_project, data=data, statuses=statuses)
        return
    status_id = manager.get_status_id(status)
    data.append(status_id)
    manager.insert_project([tuple(data)])
    bot.send_message(message.chat.id, "Проект сохранен 🧏🏻‍♀️", reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=['skills'])
def skill_handler(message):
    user_id = message.from_user.id
    projects = manager.get_projects(user_id)
    if projects:
        projects = [x[2] for x in projects]
        bot.send_message(message.chat.id, 'Выбери проект для которого нужно выбрать навык:', reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, skill_project, projects=projects)
    else:
        no_projects(message)


def skill_project(message, projects):
    project_name = message.text
    if message.text == cancel_button:
        canсel(message)
        return
        
    if project_name not in projects:
        bot.send_message(message.chat.id, 'У тебя нет такого проекта, попробуй еще раз!🫢 Выбери проект для которого нужно выбрать навык:', reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, skill_project, projects=projects)
    else:
        skills = [x[1] for x in manager.get_skills()]
        bot.send_message(message.chat.id, 'Выбери навык:', reply_markup=gen_markup(skills))
        bot.register_next_step_handler(message, set_skill, project_name=project_name, skills=skills)

def set_skill(message, project_name, skills):
    skill = message.text
    user_id = message.from_user.id
    if message.text == cancel_button:
        canсel(message)
        return
        
    if skill not in skills:
        bot.send_message(message.chat.id, 'Видимо, ты выбрал навык. не из спика, попробуй еще раз!🫢 Выбери навык:', reply_markup=gen_markup(skills))
        bot.register_next_step_handler(message, set_skill, project_name=project_name, skills=skills)
        return
    manager.insert_skill(user_id, project_name, skill )
    bot.send_message(message.chat.id, f'Навык {skill} добавлен проекту {project_name}', reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=['projects'])
def get_projects(message):
    user_id = message.from_user.id
    projects = manager.get_projects(user_id)
    if projects:
        text = "\n".join([f"Project name:{x[2]} \nLink:{x[4]}\n" for x in projects])
        bot.send_message(message.chat.id, text, reply_markup=gen_inline_markup([x[2] for x in projects]))
    else:
        no_projects(message)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    project_name = call.data
    info_project(call.message, call.from_user.id, project_name)


@bot.message_handler(commands=['delete'])
def delete_handler(message):
    user_id = message.from_user.id
    projects = manager.get_projects(user_id)
    if projects:
        text = "\n".join([f"Project name:{x[2]} \nLink:{x[4]}\n" for x in projects])
        projects = [x[2] for x in projects]
        bot.send_message(message.chat.id, text, reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, delete_project, projects=projects)
    else:
        no_projects(message)

def delete_project(message, projects):
    project = message.text
    user_id = message.from_user.id

    if message.text == cancel_button:
        canсel(message)
        return
    if project not in projects:
        bot.send_message(message.chat.id, 'У тебя нет такого проекта, попробуй выбрать еще раз!', reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, delete_project, projects=projects)
        return
    project_id = manager.get_project_id(project, user_id)
    manager.delete_project(user_id, project_id)
    bot.send_message(message.chat.id, f'Проект {project} удален!', reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=['update_projects'])
def update_project(message):
    user_id = message.from_user.id
    projects = manager.get_projects(user_id)
    if projects:
        projects = [x[2] for x in projects]
        bot.send_message(message.chat.id, "Выбери проект, который хочешь изменить", reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, update_project_step_2, projects=projects )
    else:
        no_projects(message)

def update_project_step_2(message, projects):
    project_name = message.text
    if message.text == cancel_button:
        canсel(message)
        return
    if project_name not in projects:
        bot.send_message(message.chat.id, "Что-то пошло не так!) Выбери проект, который хочешь изменить еще раз:", reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, update_project_step_2, projects=projects )
        return
    bot.send_message(message.chat.id, "Выбери, что требуется изменить в проекте", reply_markup=gen_markup(attributes_of_projects.keys()))
    bot.register_next_step_handler(message, update_project_step_3, project_name=project_name)

def update_project_step_3(message, project_name):
    attribute = message.text
    reply_markup = None 
    if message.text == cancel_button:
        canсel(message)
        return
    if attribute not in attributes_of_projects.keys():
        bot.send_message(message.chat.id, "Кажется, ты ошибся, попробуй еще раз!)", reply_markup=gen_markup(attributes_of_projects.keys()))
        bot.register_next_step_handler(message, update_project_step_3, project_name=project_name)
        return
    elif attribute == "Статус":
        rows = manager.get_statuses()
        reply_markup=gen_markup([x[0] for x in rows])
    bot.send_message(message.chat.id, attributes_of_projects[attribute][0], reply_markup = reply_markup)
    bot.register_next_step_handler(message, update_project_step_4, project_name=project_name, attribute=attributes_of_projects[attribute][1])

def update_project_step_4(message, project_name, attribute): 
    update_info = message.text
    if attribute== "status_id":
        rows = manager.get_statuses()
        if update_info in [x[0] for x in rows]:
            update_info = manager.get_status_id(update_info)
        elif update_info == cancel_button:
            canсel(message)
        else:
            bot.send_message(message.chat.id, "Был выбран неверный статус, попробуй еще раз!)", reply_markup=gen_markup([x[0] for x in rows]))
            bot.register_next_step_handler(message, update_project_step_4, project_name=project_name, attribute=attribute)
            return
    user_id = message.from_user.id
    data = (update_info, project_name, user_id)
    manager.update_projects(attribute, data)
    bot.send_message(message.chat.id, "Готово! Обновления внесены!)", reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=['update_status'])
def update_project_status(message):
    user_id = message.from_user.id
    projects = [x[2] for x in manager.get_projects(user_id)]
    if not projects:
        no_projects(message)
        return
    bot.send_message(message.chat.id, "Выберите проект, статус которого нужно изменить:", reply_markup=gen_markup(projects))
    bot.register_next_step_handler(message, process_update_project_status_select_project, projects=projects)

def process_update_project_status_select_project(message, projects):
    project_name = message.text
    if project_name == cancel_button:
        canсel(message)
        return
    if project_name not in projects:
        bot.send_message(message.chat.id, "Проект не найден. Попробуйте еще раз.", reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, process_update_project_status_select_project, projects=projects)
        return
    statuses = [x[0] for x in manager.get_statuses()]
    bot.send_message(message.chat.id, "Выберите новый статус для проекта:", reply_markup=gen_markup(statuses))
    bot.register_next_step_handler(message, process_update_project_status_select_status, project_name=project_name)

def process_update_project_status_select_status(message, project_name):
    new_status_name = message.text
    if new_status_name == cancel_button:
        canсel(message)
        return
    new_status_id = manager.get_status_id(new_status_name)
    if new_status_id is None:
        bot.send_message(message.chat.id, "Статус не найден. Попробуйте еще раз.", reply_markup=types.ReplyKeyboardRemove())
        return
    user_id = message.from_user.id
    data = (new_status_id, project_name, user_id)
    manager.update_projects("status_id", data)
    bot.send_message(message.chat.id, f"Статус проекта '{project_name}' изменен на '{new_status_name}'!", reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=['delete_status'])
def delete_project_status(message):
    user_id = message.from_user.id
    projects = [x[2] for x in manager.get_projects(user_id)]
    if not projects:
        no_projects(message)
        return
    bot.send_message(message.chat.id, "Выберите проект, статус которого нужно сбросить:", reply_markup=gen_markup(projects))
    bot.register_next_step_handler(message, process_delete_project_status_select_project, projects=projects)

def process_delete_project_status_select_project(message, projects):
    project_name = message.text
    if project_name == cancel_button:
        canсel(message)
        return
    if project_name not in projects:
        bot.send_message(message.chat.id, "Проект не найден. Попробуйте еще раз.", reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, process_delete_project_status_select_project, projects=projects)
        return
    user_id = message.from_user.id
    project_id = manager.get_project_id(project_name, user_id)
    manager.update_projects("status_id", (None, project_name, user_id))
    bot.send_message(message.chat.id, f"Статус проекта '{project_name}' сброшен!", reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=['delete_project_skill'])
def delete_project_skill_handler(message):
    user_id = message.from_user.id
    projects = [x[2] for x in manager.get_projects(user_id)]
    if not projects:
        no_projects(message)
        return
    bot.send_message(message.chat.id, "Выберите проект, из которого нужно удалить навык:", reply_markup=gen_markup(projects))
    bot.register_next_step_handler(message, process_delete_project_skill_select_project, projects=projects)

def process_delete_project_skill_select_project(message, projects):
    project_name = message.text
    if project_name == cancel_button:
        canсel(message)
        return
    if project_name not in projects:
        bot.send_message(message.chat.id, "Проект не найден. Попробуйте еще раз.", reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, process_delete_project_skill_select_project, projects=projects)
        return
    user_id = message.from_user.id
    project_id = manager.get_project_id(project_name, user_id)
    skills = manager.get_project_skills(project_name)
    if not skills:
        bot.send_message(message.chat.id, "В этом проекте нет навыков для удаления.", reply_markup=types.ReplyKeyboardRemove())
        return
    skills = skills.split(", ")
    bot.send_message(message.chat.id, "Выберите навык для удаления:", reply_markup=gen_markup(skills))
    bot.register_next_step_handler(message, process_delete_project_skill_select_skill, project_id=project_id, skills=skills)

def process_delete_project_skill_select_skill(message, project_id, skills):
    skill_name = message.text
    if skill_name == cancel_button:
        canсel(message)
        return
    if skill_name not in skills:
        bot.send_message(message.chat.id, "Навык не найден. Попробуйте еще раз.", reply_markup=gen_markup(skills))
        bot.register_next_step_handler(message, process_delete_project_skill_select_skill, project_id=project_id, skills=skills)
        return
    skill_id = manager.get_skill_id(skill_name)
    manager.delete_project_skill(project_id, skill_id)
    bot.send_message(message.chat.id, f"Навык '{skill_name}' удален из проекта!", reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=['update_project_skill'])
def update_project_skill_handler(message):
    user_id = message.from_user.id
    projects = [x[2] for x in manager.get_projects(user_id)]
    if not projects:
        no_projects(message)
        return
    bot.send_message(message.chat.id, "Выберите проект, в котором нужно обновить навык:", reply_markup=gen_markup(projects))
    bot.register_next_step_handler(message, process_update_project_skill_select_project, projects=projects)

def process_update_project_skill_select_project(message, projects):
    project_name = message.text
    if project_name == cancel_button:
        canсel(message)
        return
    if project_name not in projects:
        bot.send_message(message.chat.id, "Проект не найден. Попробуйте еще раз.", reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, process_update_project_skill_select_project, projects=projects)
        return
    user_id = message.from_user.id
    project_id = manager.get_project_id(project_name, user_id)
    skills = manager.get_project_skills(project_name)
    if not skills:
        bot.send_message(message.chat.id, "В этом проекте нет навыков для обновления.", reply_markup=types.ReplyKeyboardRemove())
        return
    skills = skills.split(", ")
    bot.send_message(message.chat.id, "Выберите навык для обновления:", reply_markup=gen_markup(skills))
    bot.register_next_step_handler(message, process_update_project_skill_select_skill, project_id=project_id, skills=skills)

def process_update_project_skill_select_skill(message, project_id, skills):
    old_skill_name = message.text
    if old_skill_name == cancel_button:
        canсel(message)
        return
    if old_skill_name not in skills:
        bot.send_message(message.chat.id, "Навык не найден. Попробуйте еще раз.", reply_markup=gen_markup(skills))
        bot.register_next_step_handler(message, process_update_project_skill_select_skill, project_id=project_id, skills=skills)
        return
    all_skills = [x[1] for x in manager.get_skills()]
    bot.send_message(message.chat.id, "Выберите новый навык:", reply_markup=gen_markup(all_skills))
    bot.register_next_step_handler(message, process_update_project_skill_set_new_skill, project_id=project_id, old_skill_name=old_skill_name)

def process_update_project_skill_set_new_skill(message, project_id, old_skill_name):
    new_skill_name = message.text
    if new_skill_name == cancel_button:
        canсel(message)
        return
    new_skill_id = manager.get_skill_id(new_skill_name)
    if new_skill_id is None:
        bot.send_message(message.chat.id, "Навык не найден. Попробуйте еще раз.", reply_markup=types.ReplyKeyboardRemove())
        return
    old_skill_id = manager.get_skill_id(old_skill_name)
    manager.update_project_skill(project_id, old_skill_id, new_skill_id)
    bot.send_message(message.chat.id, f"Навык '{old_skill_name}' обновлен на '{new_skill_name}'!", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda message: True)
def text_handler(message):
    user_id = message.from_user.id
    projects =[ x[2] for x in manager.get_projects(user_id)]
    project = message.text
    if project in projects:
        info_project(message, user_id, project)
        return
    bot.reply_to(message, "Тебе нужна помощь?")
    info(message)

    
if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    bot.infinity_polling()
