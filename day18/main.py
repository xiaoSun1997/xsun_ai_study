from langchain_community.document_loaders import TextLoader


def load_txt_file():
    text_loader = TextLoader("pic.txt",encoding="utf-8")
    data = text_loader.load()
    print("===txt===")
    print(data)


if __name__ == '__main__':
    load_txt_file()

# ===txt===
#[Document(metadata={'source': 'pic.txt'}, page_content='\n12345')]
