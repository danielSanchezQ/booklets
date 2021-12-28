from pathlib import Path

import PySimpleGUI as sg
import pdf


def run(path: str, size: int, progress_bar: sg.ProgressBar):
    path = Path(path)
    with open(path, "rb") as f:
        reader = pdf.PdfFileReader(f)
        bar_size, extra = divmod(reader.getNumPages(), size)
        bar_size = bar_size + 1 if extra > 0 else 0
        for i in pdf.split_pdf_with_size(path, reader, size):
            progress_bar.update(i+1, bar_size)


if __name__ == "__main__":
    # Define the window's contents
    progress_bar = sg.ProgressBar(1, bar_color=("red", "white"), orientation='h', key='PROGRESS')
    layout = [[sg.Text("Input pdf file"), sg.FileBrowse(file_types=("PDF", "*.pdf"), key="INPUT_FILE")],
              [sg.Text("Booklet size"), sg.Spin(initial_value=16, values=list(range(1, 1000)), key="SIZE")],
              [progress_bar],
              [sg.Button('Start'), sg.Button('Quit')]]

    # Create the window
    window = sg.Window('PDF booklet chop', layout)
    # Display and interact with the Window using an Event Loop
    while True:
        event, values = window.read()
        # See if user wants to quit or window was closed
        if event == sg.WINDOW_CLOSED or event == 'Quit':
            break
        if event == "Start":
            size = int(values["SIZE"])

            if path := values["INPUT_FILE"]:
                run(path, size, progress_bar)
                sg.PopupQuickMessage("Finished!")
            else:
                sg.PopupError("Please select a pdf file")

    # Finish up by removing from the screen
    window.close()
