import time

import gradio as gr

from script.scrap_tweets import tweets
from script.scrap_interactions import interactions
from script.scrap_homepages import homepages
from common import get_logger

logger = get_logger("global")

# Default configuration values
DEFAULT_CONFIG = {
    "threads": 1,
    "users": 1,
    "tweet_num": 100,
    "time_range": 240,  # in hours
    "homepage_list": ["home", "X", "elonmusk", "Tesla", "Erdayastronaut"],
    "url_list": ["https://x.com/MathVerseNFT/status/1899369827866685661", "https://x.com/MathVerseNFT/status/1874155560058196310", "https://x.com/playbuxco/status/1858547202240725383",
                 "https://x.com/Galxe/status/1901997396667638104"],
    "id_list": ["elonmusk", "NASA", "realDonaldTrump", "realDonaldTrump"],
}


def run_module1(config):
    if not all(len(sub) > 0 for sub in config["homepage_list"]):
        return gr.Info("Please input at least one homepage to crawl")
    tweets(config)
    return gr.Info("-- scrap_tweets completed --")


def run_module2(config):
    if not all(len(sub) > 0 for sub in config["url_list"]):
        return gr.Info("Please input at least one url to crawl")
    interactions(config)
    return gr.Info("-- scrap_interactions completed --")


def run_module3(config):
    if not all(len(sub) > 0 for sub in config["id_list"]):
        return gr.Info("Please input at least one id to crawl")
    homepages(config)
    return gr.Info("-- Module homepages completed --")


def collect_config_values(*args):
    return {
        "threads": args[0],
        "users": args[1],
        "tweet_num": args[2],
        "time_range": args[3],
        "homepage_list": args[4].split("\n"),
        "url_list": args[5].split("\n"),
        "id_list": args[6].split("\n"),
    }


with gr.Blocks() as demo:
    with gr.Row():
        threads = gr.Number(label="Threads", value=DEFAULT_CONFIG["threads"], precision=0, scale=2)
        users = gr.Number(label="Total Users", value=DEFAULT_CONFIG["users"], precision=0, scale=2)

    with gr.Tab("Tweets"):
        with gr.Column():
            tweets_num = gr.Number(label="Number of Tweets to Crawl", value=DEFAULT_CONFIG["tweet_num"], precision=0)
            time_range = gr.Number(label="Crawl Time Range (hours)", value=DEFAULT_CONFIG["time_range"], precision=0)

        homepage_list = gr.TextArea(label="input homepage that want to crawl (each line as an element)", placeholder="\n".join(DEFAULT_CONFIG["homepage_list"]))
        # homepage_list = gr.Text(label="input homepage that want to crawl (each line as an element)", placeholder="\n".join(DEFAULT_CONFIG["homepage_list"]))
        run_module1_btn = gr.Button(value="Run Module 1", variant="primary", elem_classes="custom-button")

        gr.Examples(
            examples=[
                ["\n".join(DEFAULT_CONFIG["homepage_list"])],
                ["home\nhome\nhome\nhome\nhome"],
            ],
            inputs=[homepage_list]
        )

    with gr.Tab("Interaction"):
        url_list = gr.TextArea(label="input url that want to crawl (each line as an element)", placeholder="\n".join(DEFAULT_CONFIG["url_list"]))
        run_module2_btn = gr.Button(value="Run Module 2", variant="primary", elem_classes="custom-button")

        gr.Examples(
            examples=[
                ["\n".join(DEFAULT_CONFIG["url_list"])]
            ],
            inputs=[url_list]
        )

    with gr.Tab("Homepage"):
        id_list = gr.TextArea(label="input url that want to crawl (each line as an element)", placeholder="\n".join(DEFAULT_CONFIG["id_list"]))
        run_module3_btn = gr.Button(value="Run Module 3", variant="primary", elem_classes="custom-button")

        gr.Examples(
            examples=[
                ["\n".join(DEFAULT_CONFIG["id_list"])]
            ],
            inputs=[id_list]
        )

    # gr.Examples(
    #     examples=[
    #         ["\n".join(DEFAULT_CONFIG["homepage_list"]), "\n".join(DEFAULT_CONFIG["url_list"]), "\n".join(DEFAULT_CONFIG["id_list"]), ]
    #     ],
    #     inputs=[homepage_list, url_list, id_list]
    # )

    output_box = gr.Markdown("", elem_classes="log-output")

    config_inputs = [
        threads, users, tweets_num, time_range, homepage_list, url_list, id_list
    ]

    run_module1_btn.click(
        fn=lambda *args: run_module1(collect_config_values(*args)),
        inputs=config_inputs
    )
    run_module2_btn.click(
        fn=lambda *args: run_module2(collect_config_values(*args)),
        inputs=config_inputs
    )
    run_module3_btn.click(
        fn=lambda *args: run_module3(collect_config_values(*args)),
        inputs=config_inputs
    )



demo.launch()
