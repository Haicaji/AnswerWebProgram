import gradio as gr
import pandas as pd
import base64
from PIL import Image
from io import BytesIO

# 题库文件路径
questions_csv_path = "Data/all_questions.csv"
# 全局变量
questions_dict = {}
current_question_index = 1
current_checked_question_index = 0
last_question_index = 1
high_worry_rate = 0
wait_question_index_list = []


def read_questions():
    global questions_dict
    df = pd.read_csv(questions_csv_path)
    # 将DataFrame转换为列表
    questions_list = df.values.tolist()
    for question in questions_list:
        questions_dict[question[0]] = question


def change_high_worry_rate(worry_rate):
    global high_worry_rate
    high_worry_rate = worry_rate * 0.01


def get_question():
    global questions_dict
    global wait_question_index_list

    num_smallest_attempts = 1

    if not wait_question_index_list:
        # 按照答题次数有小到大排序,再按照回答错误次数由大到小排序
        questions_dict_sort = sorted(questions_dict.items(), key=lambda item: (item[1][-2], -item[1][-1]))
        # 获取答题次数的前num_smallest_attempts小的题目
        unique_attempts = sorted(set(item[1][-2] for item in questions_dict_sort))
        while True:
            num_smallest_attempts_tmp = min(num_smallest_attempts, len(unique_attempts))
            selected_attempts = unique_attempts[:num_smallest_attempts_tmp]
            # 获取指定数量的最小答题次数的index
            wait_question_index_list = [item[0] for item in questions_dict_sort if item[1][-2] in selected_attempts]
            # 根据正确率过滤
            wait_question_index_list = [
                item for item in wait_question_index_list
                if questions_dict[item][8] == 0 or questions_dict[item][9] / questions_dict[item][8] >= high_worry_rate]

            if wait_question_index_list:
                break
            elif num_smallest_attempts_tmp == len(unique_attempts):
                return -1
            else:
                num_smallest_attempts += 1

    question_index = wait_question_index_list[0]
    wait_question_index_list.remove(question_index)

    return question_index


def get_previous_question():
    global current_question_index
    global last_question_index

    current_question_index = last_question_index

    questions_index = questions_dict[current_question_index][0]
    question_text, question_image = extract_base64_to_image(questions_dict[current_question_index][1])
    question_option_A_text, question_option_A_image = extract_base64_to_image(questions_dict[current_question_index][3])
    question_option_B_text, question_option_B_image = extract_base64_to_image(questions_dict[current_question_index][4])
    question_option_C_text, question_option_C_image = extract_base64_to_image(questions_dict[current_question_index][5])
    question_option_D_text, question_option_D_image = extract_base64_to_image(questions_dict[current_question_index][6])

    image = question_image + question_option_A_image + question_option_B_image + question_option_C_image + question_option_D_image

    return (questions_index,
            questions_dict[current_question_index][-2], questions_dict[current_question_index][-1],
            question_text, image,
            question_option_A_text,
            question_option_B_text,
            question_option_C_text,
            question_option_D_text,
            "", "")


def get_next_question():
    global current_question_index
    global last_question_index

    if current_question_index == last_question_index:
        current_question_index += 1
    else:
        last_question_index = current_question_index
        current_question_index = get_question()

    questions_index = questions_dict[current_question_index][0]
    question_text, question_image = extract_base64_to_image(questions_dict[current_question_index][1])
    question_option_A_text, question_option_A_image = extract_base64_to_image(questions_dict[current_question_index][3])
    question_option_B_text, question_option_B_image = extract_base64_to_image(questions_dict[current_question_index][4])
    question_option_C_text, question_option_C_image = extract_base64_to_image(questions_dict[current_question_index][5])
    question_option_D_text, question_option_D_image = extract_base64_to_image(questions_dict[current_question_index][6])

    image = question_image + question_option_A_image + question_option_B_image + question_option_C_image + question_option_D_image

    return (questions_index,
            questions_dict[current_question_index][-2], questions_dict[current_question_index][-1],
            question_text, image,
            question_option_A_text,
            question_option_B_text,
            question_option_C_text,
            question_option_D_text,
            "", "")


def check_answer(options):
    global current_question_index
    global current_checked_question_index

    if current_checked_question_index != current_question_index:
        current_checked_question_index = current_question_index
        questions_dict[current_question_index][8] += 1
        if options == questions_dict[current_question_index][2]:
            pass
        else:
            questions_dict[current_question_index][9] += 1

    return (questions_dict[current_question_index][2], questions_dict[current_question_index][7],
            questions_dict[current_question_index][-2], questions_dict[current_question_index][-1])


def save_record():
    global questions_dict
    new_columns_order = ['question_id', 'question', 'answer', 'A', 'B', 'C', 'D', 'explain', 'answer_time',
                         'worry_time']
    questions_list_s = questions_dict.values()

    df_s = pd.DataFrame(questions_list_s, columns=new_columns_order)
    df_s.to_csv(questions_csv_path, index=False, encoding="utf_8")


def extract_base64_to_image(text):
    if '[image:base64]' in text:
        [text, images_base64] = text.split('[image:base64]')
    else:
        image = r'E:\PythonFile\--AnswerProgram\tmp\img.png'
        text = text
        return text, []

    if '|' in images_base64:
        images_base64 = images_base64.split('|')
    else:
        images_base64 = [images_base64]

    images = []
    for image_base64 in images_base64:
        # base64解码
        image_data = base64.b64decode(image_base64)
        # 转换为图像
        image = Image.open(BytesIO(image_data))
        images.append(image)

    return text, images


def modify_sava(question_textbox,
                A_option_textbox, B_option_textbox, C_option_textbox, D_option_textbox,
                answer_textbox, explain_textbox):
    global current_question_index
    global questions_dict

    questions_dict[current_question_index][1] = question_textbox
    questions_dict[current_question_index][3] = A_option_textbox
    questions_dict[current_question_index][4] = B_option_textbox
    questions_dict[current_question_index][5] = C_option_textbox
    questions_dict[current_question_index][6] = D_option_textbox
    if answer_textbox != '':
        questions_dict[current_question_index][2] = answer_textbox
    if explain_textbox != '':
        questions_dict[current_question_index][7] = explain_textbox

    question_text, question_image = extract_base64_to_image(questions_dict[current_question_index][1])
    question_option_A_text, question_option_A_image = extract_base64_to_image(questions_dict[current_question_index][3])
    question_option_B_text, question_option_B_image = extract_base64_to_image(questions_dict[current_question_index][4])
    question_option_C_text, question_option_C_image = extract_base64_to_image(questions_dict[current_question_index][5])
    question_option_D_text, question_option_D_image = extract_base64_to_image(questions_dict[current_question_index][6])

    image = question_image + question_option_A_image + question_option_B_image + question_option_C_image + question_option_D_image

    return (question_text, image,
            question_option_A_text, question_option_B_text,
            question_option_C_text, question_option_D_text)


def main():
    global current_question_index
    global questions_dict

    read_questions()

    with gr.Blocks() as demo:
        with gr.Row():
            question_num_textbox = gr.Textbox(label="题号:  ",
                                              value='',
                                              interactive=False)
            ans_question_time_textbox = gr.Textbox(label="该题共回答次数:  ",
                                                   value='',
                                                   interactive=False)
            wrong_question_time_textbox = gr.Textbox(label="该题回答错误次数:  ",
                                                     value='',
                                                     interactive=False)
        with gr.Row():
            question_textbox = gr.Textbox(label="题目: ",
                                          value='',
                                          interactive=True)
            image = gr.Gallery(height=300)
        with gr.Row():
            A_option_textbox = gr.Textbox(label="选项A: ", value='', interactive=True)
            B_option_textbox = gr.Textbox(label="选项B: ", value='', interactive=True)
            C_option_textbox = gr.Textbox(label="选项C: ", value='', interactive=True)
            D_option_textbox = gr.Textbox(label="选项D: ", value='', interactive=True)

        options_dropdown = gr.Dropdown(choices=["A", "B", "C", "D", "不会"], label="请选择: ")

        with gr.Row():
            previous_button = gr.Button("上一题")

            check_button = gr.Button("查看答案与解析")

            save_button = gr.Button("保存做题记录")

            next_button = gr.Button("下一题")

        with gr.Row():
            answer_textbox = gr.Textbox(label="答案: ", value="", interactive=True)
            explain_textbox = gr.Textbox(label="解析: ", value="", interactive=True)

        with gr.Row():
            high_worry_rate_slider = gr.Slider(0, 100, value=0, label="题目只输出错误率大于等于:")

        with gr.Row():
            # 保存修改后的题目
            modify_sava_button = gr.Button("保存修改后的题目")

        previous_button.click(fn=get_previous_question,
                              outputs=[question_num_textbox,
                                       ans_question_time_textbox, wrong_question_time_textbox,
                                       question_textbox, image,
                                       A_option_textbox,
                                       B_option_textbox,
                                       C_option_textbox,
                                       D_option_textbox,
                                       answer_textbox, explain_textbox])
        next_button.click(fn=get_next_question,
                          outputs=[question_num_textbox,
                                   ans_question_time_textbox, wrong_question_time_textbox,
                                   question_textbox, image,
                                   A_option_textbox,
                                   B_option_textbox,
                                   C_option_textbox,
                                   D_option_textbox,
                                   answer_textbox, explain_textbox])
        save_button.click(fn=save_record, outputs=[])
        check_button.click(fn=check_answer, inputs=options_dropdown,
                           outputs=[answer_textbox, explain_textbox,
                                    ans_question_time_textbox, wrong_question_time_textbox])
        high_worry_rate_slider.change(fn=change_high_worry_rate, inputs=high_worry_rate_slider, outputs=[])
        modify_sava_button.click(fn=modify_sava,
                                 inputs=[question_textbox,
                                         A_option_textbox, B_option_textbox,
                                         C_option_textbox, D_option_textbox,
                                         answer_textbox, explain_textbox],
                                 outputs=[question_textbox, image,
                                          A_option_textbox, B_option_textbox,
                                          C_option_textbox, D_option_textbox])

    demo.launch(share=True)


if __name__ == '__main__':
    main()
