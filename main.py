import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, QLabel, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
from tictactoe import TicTacToe, MCTS  # Ensure this file is in the same directory

class TicTacToeGUI(QWidget):
    def __init__(self, game, mcts):
        super().__init__()
        self.game = game
        self.mcts = mcts
        self.state = self.game.get_initial_state()
        self.player = 1  # 1 for human (X), -1 for AI (O)
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Tic Tac Toe with AlphaZero AI")
        self.setFixedSize(350, 450)
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Status label at the top
        self.status_label = QLabel("Your Turn (X)")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 20px; color: #333; background-color: #e6e6e6; padding: 10px;")
        main_layout.addWidget(self.status_label)
        
        # Grid layout for game board
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(5)
        self.buttons = []
        for row in range(3):
            row_buttons = []
            for col in range(3):
                button = QPushButton("")
                button.setFixedSize(100, 100)
                # Set a default style for empty cells
                button.setStyleSheet("font-size: 24px; background-color: #F0F0F0;")
                button.clicked.connect(lambda checked, r=row, c=col: self.handle_click(r, c))
                self.grid_layout.addWidget(button, row, col)
                row_buttons.append(button)
            self.buttons.append(row_buttons)
        main_layout.addLayout(self.grid_layout)
        
        # Reset button at the bottom
        reset_layout = QHBoxLayout()
        self.reset_button = QPushButton("Reset Game")
        self.reset_button.setFixedSize(120, 40)
        self.reset_button.setStyleSheet("font-size: 16px; background-color: #d9d9d9;")
        self.reset_button.clicked.connect(self.reset_game)
        reset_layout.addStretch()
        reset_layout.addWidget(self.reset_button)
        reset_layout.addStretch()
        main_layout.addLayout(reset_layout)
        
        self.setLayout(main_layout)
    
    def handle_click(self, row, col):
        action = row * 3 + col
        valid_moves = self.game.get_valid_moves(self.state)
        if valid_moves[action] == 0:
            return  # Invalid move (cell already taken)
        
        # Human makes a move
        self.state = self.game.get_next_state(self.state, action, self.player)
        self.update_board()
        
        value, is_terminal = self.game.get_value_and_terminated(self.state, action)
        if is_terminal:
            self.end_game(value)
            return
        
        # Switch to AI
        self.player = self.game.get_opponent(self.player)
        self.status_label.setText("AI's Turn (O)")
        QApplication.processEvents()  # Ensure UI updates before AI starts thinking
        self.ai_move()
    
    def ai_move(self):
        neutral_state = self.game.change_perspective(self.state, self.player)
        mcts_probs = self.mcts.search(neutral_state)
        action = np.argmax(mcts_probs)
        self.state = self.game.get_next_state(self.state, action, self.player)
        self.update_board()
        
        value, is_terminal = self.game.get_value_and_terminated(self.state, action)
        if is_terminal:
            self.end_game(value)
            return
        
        # Switch back to human
        self.player = self.game.get_opponent(self.player)
        self.status_label.setText("Your Turn (X)")
    
    def update_board(self):
        # Update each button text and color based on the state
        for row in range(3):
            for col in range(3):
                cell = self.state[row, col]
                if cell == 1:
                    self.buttons[row][col].setText("X")
                    self.buttons[row][col].setStyleSheet("font-size: 24px; background-color: lightblue; color: #333;")
                elif cell == -1:
                    self.buttons[row][col].setText("O")
                    self.buttons[row][col].setStyleSheet("font-size: 24px; background-color: lightcoral; color: #333;")
                else:
                    self.buttons[row][col].setText("")
                    self.buttons[row][col].setStyleSheet("font-size: 24px; background-color: #F0F0F0;")
    
    def end_game(self, value):
        if value == 1:
            msg = "AI Win!"
            self.status_label.setStyleSheet("font-size: 20px; color: green; background-color: #e6e6e6; padding: 10px;")
        elif value == -1:
            msg = "You Wins!"
            self.status_label.setStyleSheet("font-size: 20px; color: red; background-color: #e6e6e6; padding: 10px;")
        else:
            msg = "It's a Draw!"
            self.status_label.setStyleSheet("font-size: 20px; color: #555; background-color: #e6e6e6; padding: 10px;")
        self.status_label.setText(msg)
        for row in self.buttons:
            for btn in row:
                btn.setEnabled(False)
        QMessageBox.information(self, "Game Over", msg)
    
    def reset_game(self):
        self.state = self.game.get_initial_state()
        self.player = 1
        self.update_board()
        self.status_label.setText("Your Turn (X)")
        self.status_label.setStyleSheet("font-size: 20px; color: #333; background-color: #e6e6e6; padding: 10px;")
        for row in self.buttons:
            for btn in row:
                btn.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = TicTacToe()
    args = {'C': 1.41, 'num_searches': 1000}
    mcts = MCTS(game, args)
    gui = TicTacToeGUI(game, mcts)
    gui.show()
    sys.exit(app.exec_())
