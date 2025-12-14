
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


def main():

    llm = ChatOpenAI(
        model="qwen-plus",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key="你的key"
    )

    prompt = ChatPromptTemplate.from_template(
        """
        你现在是一个面试官，需要根据候选人的职位生成3~5个问题。
        职位：{job_title}
        要求：
        - 只输出问题列表
        """
    )

    parser = StrOutputParser()

    chain = prompt | llm | parser
    while True:
        print("请输入职位：")
        job_title = input("\n")
        if job_title.lower() in ["q"]:
            print("Exit")
            break

        answer = chain.invoke({"job_title": job_title})
        print("answer:AI: ",answer)

if __name__ == "__main__":
    main()

#  控制台输出为：
# (day15venv) PS E:\code\xsun_ai_study\day15> python main.py
# 请输入职位：
#
# Java开发工程师
# answer:AI:  1. 请解释Java中的面向对象特性，并结合实际项目说明你是如何运用封装、继承和多态的。
# 2. Java中的集合框架有哪些常用类？HashMap的工作原理是什么？它在JDK 1.8中有哪些优化？
# 3. 谈谈你对Spring框架的理解，特别是Spring Bean的生命周期和依赖注入的实现方式。
# 4. 在多线程编程中，如何保证线程安全？请举例说明synchronized和ReentrantLock的区别及使用场景。
# 5. 描述一次你在项目中排查和解决JVM内存溢出问题的过程，你使用了哪些工具和方法？
# 请输入职位：
#
# Agent开发工程师
# answer:AI:  1. 请介绍你在开发智能Agent系统时常用的架构设计模式，并举例说明你在项目中是如何应用这些模式的。
#
# 2. 在多Agent协作系统中，如何处理Agent之间的通信、任务分配与冲突解决？你是否有相关实践经验？
#
# 3. 你如何评估和优化Agent的决策能力与响应性能？能否分享一个你通过调优显著提升Agent表现的案例？
#
# 4. 在构建基于大语言模型的Agent时，如何实现工具调用（Tool Calling）和外部环境交互？你使用过哪些框架或平台？
#
# 5. 面对复杂任务分解与长期记忆管理，你通常采用哪些技术手段来提升Agent的任务完成能力和上下文理解连贯性？
# 请输入职位：
#
# q
# Exit