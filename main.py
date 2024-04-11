import os
import time

import google.generativeai as genai
import textwrap
import anthropic


class TicTacToe:
    def __init__(self):
        self.board = [' ' for _ in range(9)]  # we will use a single list to represent the 3x3 board
        self.current_winner = None  # keep track of winner!

    def print_board(self):
        for i in range(3):
            print('|'.join(self.board[i * 3:(i + 1) * 3]))
            if i < 2:
                print('-+-+-')

    def available_moves(self):
        return [i for i, spot in enumerate(self.board) if spot == ' ']

    def empty_squares(self):
        return ' ' in self.board

    def make_move(self, square, letter):
        if self.board[square] == ' ':
            self.board[square] = letter
            if self.winner(square, letter):
                self.current_winner = letter
            return True
        return False

    def winner(self, square, letter):
        # check the row
        row_ind = square // 3
        row = self.board[row_ind * 3:(row_ind + 1) * 3]
        if all([spot == letter for spot in row]):
            return True
        # check the column
        col_ind = square % 3
        column = [self.board[col_ind + i * 3] for i in range(3)]
        if all([spot == letter for spot in column]):
            return True
        # check the diagonals
        if square % 2 == 0:
            diagonal1 = [self.board[i] for i in [0, 4, 8]]  # left to right diagonal
            if all([spot == letter for spot in diagonal1]):
                return True
            diagonal2 = [self.board[i] for i in [2, 4, 6]]  # right to left diagonal
            if all([spot == letter for spot in diagonal2]):
                return True
        # if all of these fail
        return False


class TicTacToe3D:
    def __init__(self):
        self.board = [[[ ' ' for _ in range(3)] for _ in range(3)] for _ in range(3)]
        self.current_winner = None

    def print_board(self):
        for i in range(3):
            for j in range(3):
                print('|'.join(self.board[i][j]))
                if j < 2:
                    print('-+-+-')
            print('\n')

    def available_moves(self):
        return [(i, j, k) for i in range(3) for j in range(3) for k in range(3) if self.board[i][j][k] == ' ']

    def empty_squares(self):
        return any(' ' in sublist for layer in self.board for sublist in layer)

    def make_move(self, square, letter):
        if self.board[square[0]][square[1]][square[2]] == ' ':
            self.board[square[0]][square[1]][square[2]] = letter
            if self.winner(square, letter):
                self.current_winner = letter
            return True
        return False

    def winner(self, square, letter):
        # check the row
        row = self.board[square[0]][square[1]]
        if all([spot == letter for spot in row]):
            return True
        # check the column
        column = [self.board[square[0]][i][square[2]] for i in range(3)]
        if all([spot == letter for spot in column]):
            return True
        # check the depth
        depth = [self.board[i][square[1]][square[2]] for i in range(3)]
        if all([spot == letter for spot in depth]):
            return True
        # check the diagonals
        if square[0] == square[1] == square[2]:
            diagonal1 = [self.board[i][i][i] for i in range(3)]  # left to right diagonal
            if all([spot == letter for spot in diagonal1]):
                return True
            diagonal2 = [self.board[2 - i][i][i] for i in range(3)]  # right to left diagonal
            if all([spot == letter for spot in diagonal2]):
                return True
        # if all of these fail
        return False


def play(game, x_player, o_player, print_game=True):
    # Print player names and their letters
    print(f"{x_player.name} is '{x_player.letter}'")
    print(f"{o_player.name} is '{o_player.letter}'")

    if print_game:
        game.print_board()

    letter = 'X'  # starting letter
    # iterate while the game still has empty squares
    while game.empty_squares():
        # get the move from the appropriate player
        if letter == 'O':
            square = o_player.get_move(game)
        else:
            square = x_player.get_move(game)
        if square == 'loss':
            print(f"{o_player.name if letter == 'X' else x_player.name} wins!")
            return
        # let's define a function to make a move!
        if game.make_move(square, letter):
            if print_game:
                print(letter + ' makes a move to square {}'.format(str(square)))
                game.print_board()
                print('')  # just empty line

            if game.current_winner:
                if print_game:
                    print(letter + ' wins!')
                if isinstance(x_player, GeminiPlayer):
                    message = f"{letter} wins!"
                    print(f"Message to AI: {message}")
                    response = x_player.chat.send_message(message)
                    print(f"AI response: {response.text}")
                if isinstance(o_player, GeminiPlayer):
                    message = f"{letter} wins!"
                    print(f"Message to AI: {message}")
                    response = o_player.chat.send_message(message)
                    print(f"AI response: {response.text}")
                return letter  # ends the loop and exits the game
            # after we made our move, we need to alternate letters
            letter = 'O' if letter == 'X' else 'X'  # switches player

        # tiny break to make things a little easier to read
        time.sleep(2)

    if print_game:
        print('It\'s a tie!')
        if isinstance(x_player, GeminiPlayer):
            message = "It's a tie!"
            print(f"Message to AI: {message}")
            response = x_player.chat.send_message(message)
            print(f"AI response: {response.text}")
        if isinstance(o_player, GeminiPlayer):
            message = "It's a tie!"
            print(f"Message to AI: {message}")
            response = o_player.chat.send_message(message)
            print(f"AI response: {response.text}")


class Player:
    def __init__(self, letter, name):
        self.letter = letter
        self.name = name

    def get_move(self, game):
        valid_square = False
        val = None
        while not valid_square:
            square = input(self.letter + '\'s turn. Input move (1-27): ')
            try:
                val = int(square) - 1  # Subtract 1 here
                move = (val // 9, (val % 9) // 3, val % 3)
                if move not in game.available_moves():
                    raise ValueError
                valid_square = True
            except ValueError:
                print('Invalid square. Try again.')
        return move


class GeminiPlayer(Player):
    def __init__(self, letter, chat):
        super().__init__(letter, 'Gemini')
        self.chat = chat
        message = "We're going to play 3D Tic Tac Toe. You're '{}'. I'll tell you the position I put on the " \
                  "board. Please reply with your move as a digit from 1-27 only.".format(letter)
        self.chat.send_message(message)

    def get_move(self, game):
        valid_square = False
        val = None
        while not valid_square:
            square = self.chat.send_message(f"{self.letter}'s turn. Input move (1-27): ").text
            try:
                val = int(square) - 1  # Subtract 1 here
                move = (val // 9, (val % 9) // 3, val % 3)
                if move not in game.available_moves():
                    raise ValueError
                valid_square = True
            except ValueError:
                print('Gemini: Invalid square. Try again.')
        return move


class ClaudePlayer(Player):
    def __init__(self, letter, client):
        super().__init__(letter, 'Claude')
        self.client = client
        self.last_move = None
        self.same_move_count = 0

    def get_move(self, game):
        valid_square = False
        val = None
        while not valid_square:
            game_state = ("The current game board is '{}'. What should be the next move for '{}'? "
                          "Here is a important rule for game is answer only 1-27 digits! Only one digit is allowed!!"
                          "If you answer that not in the range of 1-27, I don't understand."
                          "Here is example <example>1</example>").format(
                ''.join(str(item) for sublist in game.board for item in sublist), self.letter)
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                system="You're the player of 3D Tic Tac Toe game.",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": game_state}
                ]
            )
            print(f"Claude response: {message.content[0].text}")
            square = message.content[0].text
            try:
                val = int(square) - 1  # Subtract 1 here
                move = (val // 9, (val % 9) // 3, val % 3)
                if move not in game.available_moves():
                    raise ValueError
                valid_square = True
                # Check if the move is the same as the last move
                if self.last_move == val:
                    self.same_move_count += 1
                else:
                    self.same_move_count = 0
                self.last_move = val
                # If the same move is made 3 times, Claude loses
                if self.same_move_count == 3:
                    print('Claude made the same move 3 times. Claude loses.')
                    return 'loss'
            except ValueError:
                print('Claude: Invalid square. Try again.')
                print('Waiting for Claude rate limit to reset...')
                time.sleep(20)
        return move


if __name__ == '__main__':
    # Init Gemini AI
    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
    model = genai.GenerativeModel('gemini-pro')
    chat = model.start_chat()

    # Init Claude AI
    client = anthropic.Anthropic(
        api_key=os.getenv('ANTHROPIC_API_KEY')
    )

    x_player = ClaudePlayer('X', client)
    o_player = GeminiPlayer('O', chat)
    game = TicTacToe3D()
    play(game, x_player, o_player, print_game=True)
