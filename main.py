import sys
import os
import json
import random
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtGui import QPixmap, QStandardItemModel, QStandardItem, QFontDatabase, QFont
from PyQt5.QtCore import Qt

from unidecode import unidecode

class NonEditableModel(QStandardItemModel):
    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled

class PokemonApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(PokemonApp, self).__init__()
        uic.loadUi('design.ui', self)

        self.setWindowTitle("QDex")
        self.init_ui_components()
        self.configure_progress_bars()
        self.data = {}
        self.abilities = {}
        self.available_languages = []
        self.current_language = self.load_language_setting()
        self.load_data()
        self.load_custom_font()
        self.languageComboBox.currentIndexChanged.connect(self.handle_language_change)
        self.randomButton.clicked.connect(self.select_random_pokemon)
        self.pokemonTableView.selectionModel().currentChanged.connect(self.on_table_selection_changed)
        QtCore.QTimer.singleShot(0, self.set_window_size_constraints)

    def load_custom_font(self):
        """Load and set the custom font from the font folder."""
        font_path = os.path.join('font', 'pokemon-emerald-pro.otf')
        print(font_path)
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            print("Failed to load custom font.")
        else:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            self.set_font_for_application(font_family)

    def set_font_for_application(self, font_family):
        """Set the custom font for the application."""
        custom_font = QFont(font_family)
        custom_font_title = QFont(font_family)
        custom_font.setPointSize(20)
        custom_font_title.setPointSize(30)
        custom_font_title.setBold(True) 
        self.setFont(custom_font)
        self.pokemonLabel.setFont(custom_font)
        self.searchBar.setFont(custom_font)
        self.descLabel.setFont(custom_font)
        self.languageComboBox.setFont(custom_font)
        self.pokemonLabel.setFont(custom_font_title)

    def set_window_size_constraints(self):
        """Set minimum and maximum size constraints for the window."""
        self.setMinimumSize(self.size())
        self.setMaximumSize(self.size())

    def init_ui_components(self):
        """Initialize UI components and their connections."""
        self.pokemonTableView = self.findChild(QtWidgets.QTableView, 'pokemonTableView')
        self.pokemonLabel = self.findChild(QtWidgets.QLabel, 'pokemonLabel')

        self.stat_components = [
            ('hpBar', 'hpLabel'),
            ('atkBar', 'atkLabel'),
            ('defBar', 'defLabel'),
            ('spatkBar', 'spatkLabel'),
            ('spdefBar', 'spdefLabel'),
            ('spdBar', 'spdLabel')
        ]
        self.type1Label = self.findChild(QtWidgets.QLabel, 'type1Label')
        self.type2Label = self.findChild(QtWidgets.QLabel, 'type2Label')
        self.searchBar = self.findChild(QtWidgets.QLineEdit, 'searchBar')
        self.searchBar.setPlaceholderText("Search Pokémon by name...")
        self.searchBar.textChanged.connect(self.filter_table)
        self.languageComboBox = self.findChild(QtWidgets.QComboBox, 'languageComboBox')
        self.randomButton = self.findChild(QtWidgets.QPushButton, 'randomButton')
        self.descLabel = self.findChild(QtWidgets.QLabel, 'descLabel')
        self.descLabel.setWordWrap(True)

    def configure_progress_bars(self):
        """Configure the stat progress bars."""
        for bar_name, _ in self.stat_components:
            bar = self.findChild(QtWidgets.QProgressBar, bar_name)
            bar.setMinimum(0)
            bar.setMaximum(255)
            bar.setValue(0)
            bar.setTextVisible(True)
            bar.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

    def wrap_text(self, text, max_chars_per_line):
        """Wrap the text to a specific number of characters per line."""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            if len(' '.join(current_line + [word])) > max_chars_per_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                current_line.append(word)

        if current_line:
            lines.append(' '.join(current_line))

        return '\n'.join(lines)
    
    def populate_language_combobox(self):
        """Populate the language selection ComboBox."""
        self.languageComboBox.clear()
        for language in self.available_languages:
            self.languageComboBox.addItem(language)
        
        current_index = self.languageComboBox.findText(self.current_language)
        if current_index != -1:
            self.languageComboBox.setCurrentIndex(current_index)

    def handle_language_change(self):
        selected_language = self.languageComboBox.currentText()
        self.change_language(selected_language)

    def filter_table(self, text):
        """Filter the Pokémon table based on search input."""
        model = self.pokemonTableView.model()
        normalized_text = unidecode(text).lower()
        for row in range(model.rowCount()):
            pokemon_name_index = model.index(row, 0)
            pokemon_name = model.data(pokemon_name_index)
            normalized_pokemon_name = unidecode(pokemon_name).lower()
            self.pokemonTableView.setRowHidden(row, normalized_text not in normalized_pokemon_name)

    def load_data(self):
        """Load Pokémon and abilities data from files."""
        try:
            with open('pokemon_details.json', 'r') as f:
                self.data = json.load(f)

            with open('abilities.json', 'r') as f:
                self.abilities = json.load(f)

            self.available_languages = self.get_available_languages()
            self.populate_language_combobox()
            self.setup_table(self.data)
        except Exception as e:
            print(f"Error loading data: {e}")

    def get_available_languages(self):
        """Extract available languages from the loaded data."""
        languages = set()
        for details in self.data.values():
            names = details['names']
            languages.update(names.keys())
        return sorted(languages)

    def change_language(self, language):
        """Change the application's display language."""
        print(f"Changing language to: {language}")
        self.current_language = language
        self.save_language_setting(language)
        self.setup_table(self.data)

    def setup_table(self, data):
        """Setup the table view with Pokémon data."""
        model = NonEditableModel()
        model.setHorizontalHeaderLabels([''])

        for details in data.values():
            name = details['names'].get(self.current_language, 'N/A')
            model.appendRow([QStandardItem(name)])

        self.pokemonTableView.setModel(model)
        self.pokemonTableView.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.pokemonTableView.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)

        if model.rowCount() > 0:
            first_index = model.index(0, 0)
            self.pokemonTableView.selectionModel().select(first_index, QtCore.QItemSelectionModel.Select)
            self.update_ui_with_selected_pokemon(first_index)

        self.pokemonTableView.selectionModel().currentChanged.connect(self.on_table_selection_changed)

    def load_language_setting(self):
        """Load the saved language setting."""
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                return settings.get('language', 'en')
        except FileNotFoundError:
            return 'en'

    def save_language_setting(self, language):
        """Save the current language setting."""
        settings = {'language': language}
        with open('settings.json', 'w') as f:
            json.dump(settings, f, indent=4)

    def update_ui_with_selected_pokemon(self, index):
        """Update the UI with details of the selected Pokémon."""
        model = self.pokemonTableView.model()
        item = model.itemFromIndex(index)

        if item:
            pokemon_index = index.row() + 1
            pokemon_name = item.text()
            self.pokemonLabel.setText(pokemon_name)
            pokemon_details = self.data.get(f"pokemon_{pokemon_index}", {})
            self.update_abilities(pokemon_details.get('abilities', []))
            self.update_types(pokemon_details.get('types', []))
            self.update_stats(pokemon_details.get('stats', []))
            self.load_and_display_sprite(pokemon_details.get('sprite_path', ''))
            self.display_description(pokemon_details.get('descriptions', {}))
            national_pokedex_number = pokemon_details.get('national_pokedex_number', 'N/A')
            self.dexLabel.setText(f"N. {national_pokedex_number}")

        else:
            self.clear_pokemon_details()

    def display_description(self, descriptions):
        """Display Pokémon description based on current language."""
        description = descriptions.get(self.current_language, 'Description not available')
        wrapped_description = self.wrap_text(description, max_chars_per_line=50)  # Adjust as needed
        self.descLabel.setText(wrapped_description)

    def load_and_display_sprite(self, sprite_path):
        """Load and display Pokémon sprite."""
        if sprite_path and os.path.exists(sprite_path):
            pixmap = QPixmap(sprite_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(384, 384)
                self.spriteLabel.setPixmap(pixmap)
            else:
                print(f"Failed to load pixmap from {sprite_path}")
        else:
            print(f"Sprite file not found: {sprite_path}")

    def update_abilities(self, abilities):
        """Update the abilities display for the selected Pokémon."""
        ability_labels = [self.findChild(QtWidgets.QLabel, 'ability1Label'),
                          self.findChild(QtWidgets.QLabel, 'ability2Label'),
                          self.findChild(QtWidgets.QLabel, 'ability3Label')]

        for i in range(3):
            if i < len(abilities):
                ability_name = abilities[i]
                ability_info = self.abilities.get(ability_name, {})
                ability_display_name = ability_info.get(self.current_language, 'N/A')
            else:
                ability_display_name = '' 

            ability_labels[i].setText(ability_display_name)
            ability_labels[i].setVisible(True)

        for j in range(len(abilities), 3):
            ability_labels[j].setText('')
            ability_labels[j].setVisible(False)

    def update_types(self, types):
        """Update the type images for the selected Pokémon."""
        type_labels = [self.type1Label, self.type2Label]
        for i in range(2):
            if i < len(types):
                type_image_path = f"types/{types[i]}.png"
                self.load_and_display_types(type_image_path, type_labels[i])
                type_labels[i].setVisible(True)
            else:
                type_labels[i].setVisible(False)

    def update_stats(self, stats):
        """Update the stats display for the selected Pokémon."""
        for (bar_name, label_name), stat in zip(self.stat_components, stats):
            stat_name = next(iter(stat))
            base_stat = stat[stat_name]
            bar = self.findChild(QtWidgets.QProgressBar, bar_name)
            label = self.findChild(QtWidgets.QLabel, label_name)
            
            label.setText(f"{base_stat}")
            bar.setValue(base_stat)
            bar.setToolTip(f"{stat_name}: {base_stat}")
            bar.setVisible(True)

    def clear_pokemon_details(self):
        """Clear the display of Pokémon details."""
        for label_name in [name for _, name in self.stat_components] + ['type1Label', 'type2Label']:
            label = self.findChild(QtWidgets.QLabel, label_name)
            label.setVisible(False)
        
        for bar_name, _ in self.stat_components:
            bar = self.findChild(QtWidgets.QProgressBar, bar_name)
            bar.setVisible(False)

    def load_and_display_types(self, image_path, label):
        """Load an image from the given path and display it on the label."""
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(64, 64)
            label.setPixmap(pixmap)
            label.setAlignment(Qt.AlignCenter)
            label.setScaledContents(False)
            
        else:
            print(f"Failed to load image from path: {image_path}")

    def on_table_view_clicked(self, index):
        """Handle table view click event to update UI with selected Pokémon."""
        self.update_ui_with_selected_pokemon(index)

    def on_table_selection_changed(self, current, previous):
        """Handle selection change to update UI with selected Pokémon."""
        self.update_ui_with_selected_pokemon(current)

    def select_random_pokemon(self):
        """Select a random Pokémon from the table view."""
        model = self.pokemonTableView.model()
        row_count = model.rowCount()

        if row_count == 0:
            print("No Pokémon available to select.")
            return

        random_row = random.randint(0, row_count - 1)
        random_index = model.index(random_row, 0)
        self.pokemonTableView.setCurrentIndex(random_index)
        self.pokemonTableView.scrollTo(random_index)
        self.update_ui_with_selected_pokemon(random_index)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = PokemonApp()
    window.show()
    sys.exit(app.exec_())
