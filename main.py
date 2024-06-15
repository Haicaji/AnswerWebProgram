import gradio as gr
import pandas as pd

# 题库文件路径
questions_csv_path = "questions_4/all_new.csv"
# 全局变量
questions_dict = {}
current_question_index = 0
current_checked_question_index = -1

df = pd.read_csv(questions_csv_path)
# 将DataFrame转换为列表
questions_list = df.values.tolist()
for question in questions_list:
    questions_dict[question[0]] = question


def get_question():
    global questions_dict
    question_index = 0

    return question_index


def get_previous_question():
    global current_question_index

    # current_question_index = (current_question_index - 1) % len(questions_dict)
    current_question_index = get_question()
    return (questions_dict[current_question_index + 1][0], questions_dict[current_question_index + 1][1],
            questions_dict[current_question_index + 1][3], questions_dict[current_question_index + 1][4],
            questions_dict[current_question_index + 1][5], questions_dict[current_question_index + 1][6],
            "", "")


def get_next_question():
    global current_question_index

    # current_question_index = (current_question_index + 1) % len(questions_dict)
    current_question_index = get_question()
    return (questions_dict[current_question_index + 1][0], questions_dict[current_question_index + 1][1],
            questions_dict[current_question_index + 1][3], questions_dict[current_question_index + 1][4],
            questions_dict[current_question_index + 1][5], questions_dict[current_question_index + 1][6],
            "", "")


def check_answer(options):
    global current_question_index
    global current_checked_question_index

    if current_checked_question_index != current_question_index:
        current_checked_question_index = current_question_index
        questions_dict[current_question_index + 1][8] += 1
        if options == questions_dict[current_question_index + 1][2]:
            pass
        else:
            questions_dict[current_question_index + 1][9] += 1

    return questions_dict[current_question_index + 1][2], questions_dict[current_question_index + 1][7]


def save_record():
    global questions_dict
    new_columns_order = ['question_id', 'question', 'answer', 'A', 'B', 'C', 'D', 'explain', 'answer_time',
                         'worry_time']
    questions_list_s = questions_dict.values()

    df_s = pd.DataFrame(questions_list_s, columns=new_columns_order)
    df_s.to_csv("questions_4/all_new.csv", index=False, encoding="utf_8")


def main():
    global current_question_index
    global questions_dict

    with gr.Blocks() as demo:
        question_num_readonly_textbox = gr.Textbox(label="题号:  ",
                                                   value=questions_dict[current_question_index + 1][0],
                                                   interactive=False)
        question_readonly_textbox = gr.Textbox(label="题目: ",
                                               value=questions_dict[current_question_index + 1][1],
                                               interactive=False)
        with gr.Row():
            A_option_textbox = gr.Textbox(label="选项A: ", value=questions_dict[current_question_index + 1][3])
            B_option_textbox = gr.Textbox(label="选项B: ", value=questions_dict[current_question_index + 1][4])
        with gr.Row():
            C_option_textbox = gr.Textbox(label="选项C: ", value=questions_dict[current_question_index + 1][5])
            D_option_textbox = gr.Textbox(label="选项D: ", value=questions_dict[current_question_index + 1][6])

        options_dropdown = gr.Dropdown(choices=["A", "B", "C", "D"], label="请选择: ")

        with gr.Row():
            previous_button = gr.Button("上一题")

            check_button = gr.Button("查看答案与解析")

            save_button = gr.Button("保存做题记录")

            next_button = gr.Button("下一题")

        with gr.Row():
            answer_textbox = gr.Textbox(label="答案: ", value="", interactive=False)
            explain_textbox = gr.Textbox(label="解析: ", value="", interactive=False)

        previous_button.click(fn=get_previous_question,
                              outputs=[question_num_readonly_textbox, question_readonly_textbox,
                                       A_option_textbox, B_option_textbox,
                                       C_option_textbox, D_option_textbox,
                                       answer_textbox, explain_textbox])
        next_button.click(fn=get_next_question, outputs=[question_num_readonly_textbox, question_readonly_textbox,
                                                         A_option_textbox, B_option_textbox,
                                                         C_option_textbox, D_option_textbox,
                                                         answer_textbox, explain_textbox])
        save_button.click(fn=save_record, outputs=[])
        check_button.click(fn=check_answer, inputs=options_dropdown, outputs=[answer_textbox, explain_textbox])

    demo.launch()


if __name__ == '__main__':
    # print(questions_dict)
    main()
