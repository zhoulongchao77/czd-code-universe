# 说明：
# 1、启动方式：streamlit run main.py
# 2、首次启动需要输入 DeepSeek API 密钥

import streamlit as st
import os
from langchain_deepseek import ChatDeepSeek

# 检查环境变量
if not os.getenv("DEEPSEEK_API_KEY"):
    api_key = st.text_input("请输入你的 DeepSeek API 密钥", type="password")
    if api_key:
        os.environ["DEEPSEEK_API_KEY"] = api_key
else:
    api_key = os.getenv("DEEPSEEK_API_KEY")

# 初始化 Streamlit 页面
st.title("Java :blue[AI面试专家]")
st.write("\n")
st.write("_> 这是一个专业的 Java AI面试专家，能根据你对 Java 知识的回答给出评价和改进建议。_")
st.write("\n")
st.write("\n")


new_question_tag = '❓新问题：'

# 初始化消息列表
if 'messages' not in st.session_state:
    st.session_state.messages = [
        (
            "system",
            '''
            # 角色 你是一个专业的 Java 面试官，能够通过分析面试者对后端开发技术的回答情况，给出具体的回答评价和相应的改进建议。你的能力可以帮助面试者了解自己的不足，并提供有效的提升方向，从而提高面试者的水平和面试成功率。

            ## 技能
            ### 技能 1：回答评价分析
            - 从回答中提取优点和可能存在的错误或不足。
            - 以「🧠回答评价」：xxxxx 的格式提供分析结果，先指出优点，再说明不足。
            ### 技能 2：改进建议提供
            - 基于回答评价中的不足，给出具体的改进建议。
            - 以「💡改进建议」：xxxxxx 的格式提供建议内容。 
            ### 技能 3：常见问题识别
            - 识别面试中常见的关于 Java 的问题模式。
            - 提供相关的 Java 学习文档和资源链接，帮助面试者进一步巩固知识。 
            ### 技能 4：问题生成
            - 每次给出评价和建议后，提出一个新的面试问题，不要一直提问某方面的技术，要尽可能多方面覆盖。

            ## 约束 
            - 仅限于面试 Java、JVM、MySQL、Redis、ElasticSearch、后端开发、架构设计知识相关的内容。 
            - 确保提供的建议具有实际可操作性。 
            - 问完 Java 再问 JVM、数据库等，而不是一直问 Java。 
            - 保持输出格式的一致性，即「🧠回答评价」：xxxxx，「💡改进建议」：xxxxxx，新问题以 {}xxxxxx 的格式提供。内容中不能包含代码块的 markdown 语法。 
            - 仅使用可信的技术文档和资源作为参考。 
            '''.format(new_question_tag)
        ),
        (
            "assistant",
            "说一下 Java 中 String 类型和 StringBuilder 类型的区别。"
        )
    ]

# 实例化 llm
if api_key:
    try:
        llm = ChatDeepSeek(
            model="deepseek-chat",
            temperature=1,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )

        # 显示最新问题
        latest_question = st.session_state.messages[-1][1]
        st.write(f"{new_question_tag}{latest_question}")

        # 获取用户输入
        user_answer = st.text_area("请输入你的回答：")

        # 添加提交按钮
        if st.button("提交"):
            # print('enter======= {}'.format(st.session_state.messages))
            if user_answer:
                st.session_state.messages.append(("human", user_answer))

                # 流式调用模型
                response_placeholder = st.empty()
                full_response = ""
                for chunk in llm.stream(st.session_state.messages):
                    chunk_content = chunk.content
                    full_response += chunk_content
                    response_placeholder.write(full_response)

                # 显示结果
                # st.write(full_response)

                # 提取新问题
                new_question_start = full_response.find(new_question_tag)
                # print('====full_response {}'.format(full_response))
                # print('====new_question_tag {}'.format(new_question_tag))
                # print('====new_question_start {}'.format(new_question_start))
                st.session_state.messages = st.session_state.messages[:-2]

                if new_question_start != -1:
                    new_question = full_response[new_question_start + len(new_question_tag):].strip()
                    # print('===={}'.format(new_question))
                    st.session_state.messages.append(("assistant", new_question))

    except Exception as e:
        st.error(f"发生错误：{e}")
else:
    st.warning("请输入有效的 DeepSeek API 密钥。")
    