from tkinter import Tk, Button, Entry, Label, StringVar, Canvas, messagebox, constants
import yaml

with open('config.yml') as f:
    config = yaml.safe_load(f)


class HangmanGUI(Tk):

    def __init__(self, parent):
        Tk.__init__(self, parent)
        self.parent = parent
        self.address = config['address'] + ':' + config['port']
        self.initialise()
        self.prep_buttons()

    def prep_buttons(self):
        new_game = Button(self, command=print('begin new game'), text='Restart')
        new_game.grid(column=2, row=5, sticky=constants.W)

        guess_letter = Button(self, command=lambda: self.guess(True), text='Guess letter')
        guess_letter.grid(column=3, row=5, sticky=constants.W)

        guess_button = Button(self, command=lambda: self.guess(False), text='Guess word')
        guess_button.grid(column=4, row=5, sticky=constants.W)

    def initialise(self):
        self.my_word = StringVar()
        self.my_word.set("Word: ")
        # self.my_word.set("Word: " +
        #                  self.hangman.word_of_underlines(len(self.hangman.word_to_guess)))

        self.tried_so_far = StringVar()
        self.tried_so_far.set('Letters tried so far: ')

        self.guesses_left = StringVar()
        self.update_no_of_guesses()

        self.geometry('{}x{}'.format(545, 400))

        self.grid()

        word = Label(self, textvariable=self.my_word)
        word.grid(column=1, row=7, sticky=constants.W)

        tried = Label(self, textvariable=self.tried_so_far)
        tried.grid(column=1, row=8, sticky=constants.W)

        no_guesses = Label(self, textvariable=self.guesses_left)
        no_guesses.grid(column=1, row=9, sticky=constants.W)

        turtle_canvas = Canvas(self, width=300, height=450)
        # self.th = TurtleHangman(turtle_canvas)
        turtle_canvas.grid(column=1, row=10, rowspan=8, columnspan=3)

        infotext = 'Hangman frontend borrowed from AML'
        info = Label(self, text=infotext)
        info.grid(column=4, row=12, columnspan=2)

    def update_my_word(self):
        self.my_word.set('Word: ')

    def update_tried_so_far(self):
        self.tried_so_far.set('Letters tried so far: ')

    def update_no_of_guesses(self):
        self.guesses_left.set('Guesses left: ')

    def guess(self):
        title = 'Guess a letter or word'

        g_window = Tk()
        g_window.title(title)
        g_window.grid()

        entry = Entry(g_window)
        entry.grid(column=1, row=1)

        confirm = Button(g_window, command=lambda:
        self.send_input(entry.get(), g_window), text='Confirm')
        confirm.grid(column=1, row=3)

    def send_input(self, guessing_letter, user_guess, g_window):

        if user_guess.isalpha():
            if (guessing_letter and len(user_guess) > 1):
                messagebox.showerror('Error', 'Please only guess a letter')
            else:
                if guessing_letter:
                    # self.hangman.guess_letter(user_guess)
                    print('guessing letter')
                else:
                    # self.hangman.guess_word(user_guess)
                    print('guessing letter')

                g_window.destroy()
        else:
            messagebox.showerror('Error', 'Please make a valid guess')

    def award_win(self):
        messagebox.showinfo('Winner!', 'You won. Click on Restart to play again')

    def notify_loser(self):
        # messagebox.showinfo('Loser!',
        #                       'You lost. Word was *' + self.hangman.word_to_guess + '*. Click on Restart to play again')

        messagebox.showinfo('Loser!',
                              'You lost. Word was **. Click on Restart to play again')


if __name__ == "__main__":
    hg = HangmanGUI(None)
    hg.title('Hangman')
    hg.mainloop()