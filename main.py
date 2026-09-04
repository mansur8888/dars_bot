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

    # 2-bosqich: Qolgan soatni barcha o'qituvchilarga toifasidan qat'i nazar 1.5 stavkagacha (max_limit) to'ldirib chiqish
    for t in sorted_teachers:
        if remaining_hours <= 0:
            break
        can_take_more = max_limit - teacher_assignments[t['id']]
        if can_take_more > 0:
            give_more = min(remaining_hours, can_take_more)
            teacher_assignments[t['id']] += give_more
            remaining_hours -= give_more

    # Natijalarni tartiblash
    results = []
    for t in sorted_teachers:
        results.append((t, teacher_assignments[t['id']]))

    # Telegram uchun matn tayyorlash
    res_text = (
        f"📊 <b>DARS TAQSIMOTI NATIJASI (RASMIY NIZOM BO'YICHA)</b>\n\n"
        f"🔹 <b>Fan:</b> {data['subject_name']}\n"
        f"🔹 <b>Jami dars soati:</b> {total_hours} soat\n"
        f"🔹 <b>1 stavka me'yori:</b> {rate} soat (Maksimal limit: {max_limit} soat)\n"
        f"🔹 <b>O'qituvchilar soni:</b> {len(teachers)} nafar\n\n"
        f"<b>Ustuvor ketma-ketlik bo'yicha taqsimot:</b>\n"
    )
    
    for idx, (t, h) in enumerate(results, 1):
        stavka = round(h / rate, 2)
        res_text += (
            f"\n<b>{idx}. {t['fish']}</b>\n"
            f" └ Maqomi: <i>{t['status_name']} ({t['step']}-o'rin)</i>\n"
            f" └ Dars soati: <b>{h} soat</b> ({stavka} stavka)\n"
        )
    
    if remaining_hours > 0:
        res_text += f"\n⚠️ <b>Diqqat:</b> Barcha o'qituvchilar 1.5 stavka (maksimal {max_limit} soat) limitiga yetdi. Taqsimlanmay qolgan soat: <b>{remaining_hours} soat</b>."
    else:
        res_text += f"\n✅ <b>Barcha dars soatlari 1.5 stavka doirasida to'liq taqsimlandi!</b>"

    # Word (.docx) hujjati yaratish
    doc = docx.Document()
    doc.add_heading('DARS SOATLARINI TAQSIMLASH BAYONNOMASI', 0)
    doc.add_paragraph(f"Fan: {data['subject_name']}")
    doc.add_paragraph(f"Jami dars soati: {total_hours} soat (1 stavka = {rate} soat, Maksimal limit = {max_limit} soat)")
    doc.add_paragraph("Ustuvor ketma-ketlik va stavka limitlari bo'yicha taqsimot natijalari:")
    
    for idx, (t, h) in enumerate(results, 1):
        stavka = round(h / rate, 2)
        doc.add_paragraph(f"{idx}. {t['fish']} - {t['status_name']}: {h} soat ({stavka} stavka)", style='List Bullet')
    
    if remaining_hours > 0:
        doc.add_paragraph(f"Eslatma: Barcha o'qituvchilar limiti to'lib, yana {remaining_hours} soat ortib qoldi.")
    else:
        doc.add_paragraph("Soatlar to'liq taqsimlandi.")

    doc.add_paragraph("\nMaktab direktori: _______________  (Imzo)")
    
    file_path = f"dars_taqsimoti_{message.chat.id}.docx"
    doc.save(file_path)

    await message.answer(res_text, parse_mode="HTML", reply_markup=main_kb)
    
    doc_file = FSInputFile(file_path)
    await message.answer_document(doc_file, caption="📄 Tayyor rasmiy hujjat (Word formatida)")
    
    if os.path.exists(file_path):
        os.remove(file_path)
        
    await state.clear()
                            
