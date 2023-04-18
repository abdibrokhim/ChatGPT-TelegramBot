async def send_ad(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """

    Send ad to specified users

    Usage: /send_ad#1000#text
        /send = command
        #1000 = number of users to send ad to
        #text = text of ad

    """
    e_u = 0

    msg = update.message.text
    print('msg:', msg)
    
    content = msg.split('#')
    print('content:', content)

    if len(content) == 3:
        to_users = content[1]
        print('to_users:', to_users)

        txt = content[2]
        print('txt:', txt)

        tg_users = await _get_clients()

        for i in range(0, len(to_users)):
            if i % 10 == 0:
                time.sleep(1)
            try:
                msg = await context.bot.send_message(chat_id=tg_users[i]['tg_id'], text=txt, parse_mode='HTML')
                print('msg:', msg)
            except Exception as e:
                print('error:', e)
                e_u += 1

        await update.message.reply_text('ad was sent to {} users'.format(len(to_users)-e_u))
    else:
        await update.message.reply_text('wrong format\nUsage: /send_ad#1000#ad')