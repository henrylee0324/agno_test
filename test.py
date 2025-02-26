"""
audio_file_path = r"C:\Users\User\Desktop\CathayAgent_prototype\test.mp3"
text_prompt = speech_processor.process_audio(audio_file_path)
if text_prompt:
    text_prompt = text_prompt
else:
text_prompt_2 = " 有多少人或組織跟川普之間有利害關係?請給我清單。"

#print(text_prompt)
v2m_team = initv2m()
response_text = ""
for response in v2m_team.ask(text_prompt):
    response_text += response  # 拼接片段
print(response_text.strip())  # 去除多餘空格
"""