学习 TextLoader / PDFLoader

# TextLoader / PDFLoader 概述

TextLoader 和 PDFLoader 是 LangChain 中的两个数据加载器（Loader），它们负责从外部文件中加载文本内容并进行处理。它们通常用于从文本文件或 PDF 文件中提取数据，然后将这些数据传递给后续的处理步骤，比如文本分析、信息提取、文档问答等。

- TextLoader 主要用于加载普通文本文件。

- PDFLoader 专门用于加载 PDF 格式的文件。

这两个加载器常常是使用文档处理任务（例如 RAG，基于文档的问答）时的第一步，它们能够从原始文档中提取出有用的内容，并将其转换为模型可以理解和处理的格式。

---
## TextLoader 基本概念

1. 功能：

    - TextLoader 主要用于从文本文件（如 .txt 文件）中加载文本内容，并将其提取为字符串数据。

    - 它可以处理简单的文本文件，也可以处理经过格式化的文档。

2. 用途：

    - 将本地文本数据加载进来，进行分析、查询、信息抽取等操作。

    - 在问答系统中，可以将文件中的内容提供给模型，进行基于文件的问答（RAG）。

---
## PDFLoader 基本概念

1. 功能：

    - PDFLoader 专门用于从 PDF 格式的文件中提取文本。

    - 它会自动处理 PDF 中的内容，去除格式、提取文字信息，并提供纯文本内容。

2. 用途：

    - 提取 PDF 中的文本信息用于后续分析，尤其是在数据科学、法律文档、学术论文等场景中，PDF 格式是常见的数据格式。

    - 可以与 TextLoader 一起使用，将多种格式的文件（如 TXT 和 PDF）整合到一起进行处理。

---
## 如何使用 TextLoader 和 PDFLoader

TextLoader 和 PDFLoader 的使用方式大致相同。你只需要提供文件路径，然后它们会自动处理文件并返回文本数据。你可以将这些数据传递给其他组件（如嵌入模型、信息检索系统等）进行进一步分析。

___

## Demo：

假设我们有两个文件：

- 一个文本文件（.txt），其中包含一篇文章。

- 一个 PDF 文件（.pdf），包含另一篇文章。

我们将使用 TextLoader 加载文本文件，使用 PDFLoader 加载 PDF 文件，然后打印出加载的内容。

### 步骤：

1. 创建一个 .txt 文件和一个 .pdf 文件。

2. 使用 TextLoader 和 PDFLoader 加载这些文件。

3. 打印加载的文本内容。

安装依赖：

首先，你需要安装 LangChain 库和 PDF 处理相关的依赖。

    pip install langchain pdfplumber langchain-community


pdfplumber 用于从 PDF 文件中提取文本内容。

Demo 代码：
```python


# file: demo_loader.py

from langchain_community.document_loaders import TextLoader, PDFLoader

def load_text_file():
    # 1. 使用 TextLoader 加载 TXT 文件
    text_loader = TextLoader('sample_text.txt', encoding='utf-8')  # 假设 sample_text.txt 是一个存在的文本文件
    text_data = text_loader.load()  # 加载文本内容
    print("=== 文本文件内容 ===")
    print(text_data[0].page_content)  # 打印加载的内容

def load_pdf_file():
    # 2. 使用 PDFLoader 加载 PDF 文件
    pdf_loader = PDFLoader('sample_pdf.pdf')  # 假设 sample_pdf.pdf 是一个存在的 PDF 文件
    pdf_data = pdf_loader.load()  # 加载 PDF 内容
    print("\n=== PDF 文件内容 ===")
    print(pdf_data[0].page_content)  # 打印加载的内容

def main():
    # 加载文本文件和 PDF 文件
    load_text_file()
    load_pdf_file()

if __name__ == "__main__":
    main()
```

代码讲解：

1. TextLoader：

- 使用 TextLoader 加载 .txt 文件，指定文件路径和编码格式（通常使用 utf-8）。

- 调用 text_loader.load() 来加载文件内容。load() 返回一个文档列表，包含了加载的每个页面或段落。对于普通的文本文件，我们通常只有一个文档对象。

- 打印出文档的内容：text_data[0].page_content 获取文本内容。

2. PDFLoader：

- 使用 PDFLoader 加载 .pdf 文件，指定文件路径。

- 调用 pdf_loader.load() 来提取 PDF 内容。load() 返回一个包含页面文本的文档列表。

- 打印出第一个页面的内容：pdf_data[0].page_content 获取 PDF 中提取的文本内容。

3. 主程序： 在 main 函数中，先后调用 load_text_file() 和 load_pdf_file() 来加载和打印两个文件的内容。

文件准备：

创建一个名为 sample_text.txt 的文本文件，内容类似：

    这是一个文本文件的示例。
    它包含了几行简单的文字，用于展示如何使用 TextLoader 加载文本。
    
    
创建一个名为 sample_pdf.pdf 的 PDF 文件，内容类似：
    
    这是一篇 PDF 文件的示例。
    它包含了几页文字，用于展示如何使用 PDFLoader 加载 PDF 文件。