async def calculate_and_show(message: types.Message, state: FSMContext, data: dict, teachers: list):
    rate = data['rate'] # 18 yoki 20 soat (1 stavka)
    max_limit = data['max_limit'] # 27 yoki 30 soat (1.5 stavka)
    total_hours = data['total_hours']
    
    # Rasmiy 10 ta ketma-ketlik bo'yicha saralash
    sorted_teachers = sorted(teachers, key=lambda x: x['step'])
    
    remaining_hours = total_hours
    teacher_assignments = {t['id']: 0 for t in sorted_teachers}

    # 1-bosqich: Ustuvorlik bo'yicha har bir o'qituvchiga dastlab 1 stavkadan (rate) taqsimlab chiqish
    for t in sorted_teachers:
        if remaining_hours <= 0:
            break
        give = min(remaining_hours, rate)
        teacher_assignments[t['id']] += give
        remaining_hours -= give

    # 2-bosqich: Agar soat ortib qolgan bo'lsa, ustuvorligiga qarab har bir o'qituvchini 1.5 stavkagacha (max_limit) to'ldirib chiqish
    if remaining_hours > 0:
        for t in sorted_teachers:
            if remaining_hours <= 0:
                break
            can_take_more = max_limit - teacher_assignments[t['id']]
            if can_take_more > 0:
                give_more = min(remaining_hours, can_take_more)
                teacher_assignments[t['id']] += give_more
                remaining_hours -= give_more

    # 3-bosqich (Muhim tuzatish): Agar shunda ham soat ortib qolsa (ya'ni barcha o'qituvchilar 1.5 stavka bo'lib qolsa ham soat oshib yotgan bo'lsa), 
    # o'qituvchilar soni yetishmagani uchun oxirgi o'qituvchilarga yoki ustuvorlarga qoldiqni bo'lib berib, soatni 0 qilish
    if remaining_hours > 0:
        for t in sorted_teachers:
            if remaining_hours <= 0:
                break
            # Mutlaq cheklangan limitdan oshmagan holda qoldiqni taqsimlaymiz (yoki ehtiyojga qarab yopamiz)
            teacher_assignments[t['id']] += remaining_hours
            remaining_hours = 0
            
