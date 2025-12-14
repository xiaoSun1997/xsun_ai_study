from transformers import pipeline


def main():
    sentiment_pipe = pipeline("sentiment-analysis")

    result_single = sentiment_pipe("I love you")
    print("Single sentence result:")
    print(result_single)
# 输出：
# Device set to use cpu
# Single sentence result:
# [{'label': 'POSITIVE', 'score': 0.9998656511306763}]
    texts = [
        "你谁啊？",
        "就瞅你，瞅你咋地！"
    ]
    result_batch = sentiment_pipe(texts)
    print("Batch result:")

    for text, result in zip(texts, result_batch):
        print(f"{text}: {result}")
        print(f"  → label: {result['label']}, score: {result['score']:.4f}")


if __name__ == "__main__":
    main()