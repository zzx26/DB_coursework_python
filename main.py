import tkinter as tk
from tkinter import ttk
import sqlite3 as sql
import os.path

root_size = '960x540+50+50'
table_window_size = '1280x620+50+50'
bg_color = '#888888'


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.iconbitmap('Spotify_icon.ico')
        self._img = tk.PhotoImage(file="pablo.gif")
        self.title('Я вам не Spotify и не Last FM')
        self.mode = 'Artist'
        self.images_array = []
        self.table_width = 0
        self.counter = 0
        self.current_artist_id = 0
        self.current_album_name = ""

        self['bg'] = bg_color

        self.Frm = ttk.Frame(self)
        ttk.Label(self.Frm, text='Search:').pack(side=tk.TOP)
        self.search_string = tk.StringVar()
        self.text_field_search = ttk.Entry(self.Frm, width=30, textvariable=self.search_string)
        self.text_field_search.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.text_field_search.focus_set()
        self.text_field_search.insert(tk.END, 'song, album or artist name')

        self.Frm2 = ttk.Frame(self)
        self.label_from_var = tk.StringVar()
        self.label_from_var.set("Click column")
        self.label_from = ttk.Label(self.Frm2, textvariable=self.label_from_var)
        self.label_from.pack(side=tk.LEFT, expand=1)

        self.search_string_from = tk.StringVar()
        self.text_field_from = ttk.Entry(self.Frm2, width=10, textvariable=self.search_string_from)
        self.text_field_from.pack(side=tk.LEFT, expand=1)
        self.text_field_from.insert(tk.END, '')

        self.label_to = ttk.Label(self.Frm2, text="To")
        self.label_to.pack(side=tk.LEFT, expand=1)

        self.search_string_to = tk.StringVar()
        self.text_field_to = ttk.Entry(self.Frm2, width=10, textvariable=self.search_string_to)
        self.text_field_to.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.text_field_to.insert(tk.END, '')

        self.search_button = ttk.Button(self.Frm, text='Find')
        self.search_button.pack(side=tk.TOP)
        self.Frm.pack()
        self.Frm2.pack()

        self.search_button.config(command=self.find)

        self.con = sql.connect('DB_music.db')
        self.cur = self.con.cursor()

        self.geometry(table_window_size)
        self['bg'] = bg_color

        self.table_frame = tk.Frame(self)
        self.table_frame.pack()

        # scrollbar
        self.table_scroll = tk.Scrollbar(self.table_frame)
        self.table_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.table_treeview = ttk.Treeview(self.table_frame, yscrollcommand=self.table_scroll.set,
                                           xscrollcommand=self.table_scroll.set)
        self.table_treeview.pack()

        self.table_scroll.config(command=self.table_treeview.yview)
        self.table_scroll.config(command=self.table_treeview.xview)

        # columns
        self.column_names_playlist_mode = ["Song Name", "Album Name", "Duration", "Artist Name", "Release Year",
                                           "Genre", "Label", "Listeners", "Times Played Live"]
        self.column_names_artist_mode = ["Artist Name", "Genre"]
        self.column_names_album_mode = ["Album Name", "Label", "Release Year"]
        self.column_names_track_mode = ["№", "Song Name", "Duration", "Listeners", "Times Played Live"]
        self.column_int_sort = ["#3", "#5", "#8", "#9"]
        self.column_str_sort = ["#1", "#2", "#4", "#6", "#7"]
        self.column_int_sort_dict = {"#3": "DURATION SPECIAL CASE", "#5": "Albums.ReleaseYearID",
                                     "#8": "Songs.Listeners", "#9": "Songs.TimedPlayedLive"}
        self.column_str_sort_dict = {"#1": "Songs.SongName", "#2": "Albums.AlbumName", "#4": "Artists.ArtistName",
                                     "#6": "Artists.Genre", "#7": "Albums.LabelName"}
        self.column_int_sort_dict_label = {"#3": "Duration", "#5": "Release Year", "#8": "Listeners",
                                           "#9": "Times Played Live"}
        self.column_str_sort_dict_label = {"#1": "Song Name", "#2": "Album Name", "#4": "Artist Name", "#6": "Genre",
                                           "#7": "Label Name"}
        self.column_click_counter = False
        self.int_parameter_search = False
        self.playlist_alive = False
        try:
            self.cur.execute('''SELECT * FROM Playlist''')
            self.playlist_alive = True
        except:
            pass
        self.playlist_open = False

        self.artist_view_entry()

        self.table_treeview.bind("<Double-1>", self.OnDoubleClick)
        self.table_treeview.bind("<Button-1>", self.OnSingularClick)

    def OnSingularClick(self, event):
        self.column_click_counter = not self.column_click_counter
        self.int_parameter_search = True
        if self.mode == 'Search':
            region = self.table_treeview.identify("region", event.x, event.y)
            column = self.table_treeview.identify_column(event.x)
            if region == "heading":
                if column in self.column_str_sort:
                    self.label_from_var.set("Search by {} From".format(self.column_str_sort_dict_label[column]))
                    self.find(order_string=self.column_str_sort_dict[column])
                elif column in self.column_int_sort:
                    self.int_parameter_search = True
                    self.label_from_var.set("Search by {} From".format(self.column_int_sort_dict_label[column]))
                    self.find(order_string=self.column_int_sort_dict[column])
                else:
                    self.label_from_var.set("Click column")

    def OnDoubleClick(self, event):
        curr_item = self.table_treeview.focus()
        if self.mode == 'Artist':
            self.album_view_entry(int(curr_item) + 1)
            self.current_artist_id = int(curr_item) + 1
        elif self.mode == 'Album':
            self.current_album_name = self.table_treeview.item(curr_item)['values'][0]
            self.track_view_entry(int(curr_item) + 1)
        elif self.mode == 'Track':
            pass
        else:
            pass

    def go_back_callback(self):
        self.label_from_var.set("Click column")
        if self.mode == 'Album':
            self.artist_view_entry()
            self.mode = 'Artist'
        elif self.mode == 'Track':
            self.album_view_entry(self.current_artist_id)
            self.mode = 'Album'
        elif self.mode == 'Search':
            self.artist_view_entry()
            self.mode = 'Artist'
        else:
            self.artist_view_entry()
            self.mode = 'Artist'

    def find(self, order_string=""):
        self.images_array.clear()
        self.mode = 'Search'
        self.entry_tree_constructor(self.column_names_playlist_mode)

        from_str = self.search_string_from.get()
        to_str = self.search_string_to.get()

        between_string = ""

        substr1 = '''SELECT * FROM Main INNER JOIN Songs ON Main.SongID = Songs.SongID 
                            INNER JOIN Albums ON Songs.AlbumID = Albums.AlbumID 
                            INNER JOIN Artists ON Albums.ArtistID = Artists.ArtistID 
                            WHERE (LOWER( Songs.SongName ) LIKE "%'''
        substr_search = self.search_string.get()
        substr_search = substr_search.lower()
        substr_end = '''%")'''
        substr2 = '''%" OR LOWER( Artists.ArtistName ) LIKE "%'''
        substr3 = '''%" OR LOWER( Albums.AlbumName ) LIKE "%'''
        if order_string != "":
            print(from_str, to_str)
            if self.int_parameter_search:
                if order_string != "DURATION SPECIAL CASE":
                    ord_field_text = order_string.replace("Search by", "")
                    ord_field_text = ord_field_text.replace(" From", "")
                    if from_str != "" and to_str != "":
                        if from_str == to_str:
                            between_string = " AND ({} = {}) ".format(ord_field_text, from_str)
                        else:
                            between_string = " AND ({} BETWEEN {} AND {}) ".format(ord_field_text, from_str, to_str)
                    elif from_str != "":
                        between_string = " AND ({} > {}) ".format(ord_field_text, from_str)
                    elif to_str != "":
                        between_string = " AND ({} < {}) ".format(ord_field_text, to_str)
                    else:
                        pass
            if self.column_click_counter:
                if order_string != "DURATION SPECIAL CASE":
                    order_string = '''ORDER BY ''' + order_string + ''' DESC'''
                else:
                    order_string = '''ORDER BY Songs.DurationMins DESC, Songs.DurationSecs DESC'''
            else:
                if order_string != "DURATION SPECIAL CASE":
                    order_string = '''ORDER BY ''' + order_string + ''' ASC'''
                else:
                    order_string = '''ORDER BY Songs.DurationMins ASC, Songs.DurationSecs ASC'''
        query = substr1 + substr_search + substr2 + substr_search + substr3 + substr_search + substr_end + between_string + order_string + ''';'''
        print(query)
        self.cur.execute(query)
        result = self.cur.fetchall()
        self.counter = 0
        for row in result:
            img_name = "album_icons/" + row[10] + ".gif"
            img_name = img_name.replace(" ", "")
            time_str = str(row[3]) + ":"
            if row[4] < 10:
                time_str = time_str + "0"
            time_str = time_str + str(row[4])
            if os.path.isfile(img_name):
                self.images_array.append(tk.PhotoImage(file=img_name))
            else:
                self.images_array.append(tk.PhotoImage(file="pablo.gif"))
            self.table_treeview.insert(parent='', index='end', iid=row[0] - 1, text="",
                                       image=self.images_array[self.counter],
                                       values=(
                                           row[2], row[10], time_str, row[15], row[12], row[16], row[11], row[5],
                                           row[6]))
            self.counter += 1

    def artist_view_entry(self):
        self.images_array.clear()
        self.mode = 'Artist'
        self.entry_tree_constructor(self.column_names_artist_mode)
        self.cur.execute('''SELECT * FROM Artists;''')
        result = self.cur.fetchall()
        self.counter = 0
        for row in result:
            img_name = "artist_icons/" + row[1] + ".gif"
            img_name = img_name.replace(" ", "")
            if os.path.isfile(img_name):
                self.images_array.append(tk.PhotoImage(file=img_name))
            else:
                self.images_array.append(tk.PhotoImage(file="pablo.gif"))
            self.table_treeview.insert(parent='', index='end', iid=row[0] - 1, text="",
                                       image=self.images_array[row[0] - 1],
                                       values=(row[1], row[2]))
            self.counter += 1

    def album_view_entry(self, ArtistID):
        self.images_array.clear()
        self.mode = 'Album'
        self.entry_tree_constructor(self.column_names_album_mode)

        self.cur.execute("SELECT * FROM Albums WHERE Albums.ArtistID=" + str(ArtistID) + ";")
        result = self.cur.fetchall()
        self.cur.execute('''SELECT SUM(Songs.TimedPlayedLive) FROM Songs INNER JOIN Albums ON Songs.AlbumID =
         Albums.AlbumID WHERE Albums.AlbumID = {} GROUP BY ALbums.AlbumID;'''.format(ArtistID))
        live_count = self.cur.fetchall()
        self.title("{} live songs".format(live_count[0][0]))
        self.counter = 0
        for row in result:
            img_name = "album_icons/" + row[1] + ".gif"
            img_name = img_name.replace(" ", "")
            if os.path.isfile(img_name):
                self.images_array.append(tk.PhotoImage(file=img_name))
            else:
                self.images_array.append(tk.PhotoImage(file="pablo.gif"))
            self.table_treeview.insert(parent='', index='end', iid=row[0] - 1, text="",
                                       image=self.images_array[self.counter],
                                       values=(row[1], row[2], row[3]))
            self.counter += 1

    def track_view_entry(self, AlbumID):
        self.images_array.clear()
        self.mode = 'Track'
        self.entry_tree_constructor(self.column_names_track_mode)

        self.cur.execute("SELECT * FROM Songs WHERE Songs.AlbumID=" + str(AlbumID) + ";")
        result = self.cur.fetchall()
        self.counter = 0
        img_name = "album_icons/" + self.current_album_name + ".gif"
        img_name = img_name.replace(" ", "")
        if os.path.isfile(img_name):
            self.images_array.append(tk.PhotoImage(file=img_name))
        else:
            self.images_array.append(tk.PhotoImage(file="pablo.gif"))
        for row in result:
            time_str = str(row[2]) + ":"
            if row[3] < 10:
                time_str = time_str + "0"
            time_str = time_str + str(row[3])
            self.table_treeview.insert(parent='', index='end', iid=row[0] - 1, text="",
                                       image=self.images_array[0],
                                       values=(row[6], row[1], time_str, row[4], row[5]))
            self.counter += 1

    def entry_tree_constructor(self, names):
        for i in self.table_treeview.get_children():
            self.table_treeview.delete(i)
        try:
            self.table_scroll.destroy()
            self.table_frame.destroy()
            self.back_button.destroy()
            self.playlist_button.destroy()
            self.add_to_playlist_button.destroy()
        except:
            pass

        self.title('Я вам не Spotify и не Last FM')
        self.table_frame = tk.Frame(self)
        self.table_frame.pack()

        # scrollbar
        self.table_scroll = tk.Scrollbar(self.table_frame)
        self.table_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.table_treeview = ttk.Treeview(self.table_frame, yscrollcommand=self.table_scroll.set,
                                           xscrollcommand=self.table_scroll.set)
        self.table_treeview.pack()

        self.table_scroll.config(command=self.table_treeview.yview)
        self.table_scroll.config(command=self.table_treeview.xview)

        self.table_treeview['columns'] = tuple(names)
        self.table_treeview.column("#0", width=30, stretch=tk.NO)
        self.table_width = int(1260 / len(names))
        for name in names:
            self.table_treeview.column(name, anchor=tk.CENTER, width=self.table_width)

        self.table_treeview.heading("#0", text="", anchor=tk.CENTER)
        for name in names:
            self.table_treeview.heading(name, text=name, anchor=tk.CENTER)

        self.table_treeview.bind("<Double-1>", self.OnDoubleClick)
        self.table_treeview.bind("<Button-1>", self.OnSingularClick)

        self.back_button = ttk.Button(self, text='Go Back', command=self.go_back_callback)
        self.back_button.pack(expand=True)

        self.playlist_button = ttk.Button(self,
                                          text='Create Playlist',
                                          command=self.create_playlist_wrapper)

        self.add_to_playlist_button = ttk.Button(self,
                                                 text='Add To Playlist',
                                                 command=self.add_song_to_playlist)
        try:
            self.cur.execute('''SELECT * FROM Playlist''')
            self.playlist_alive = True
        except:
            self.playlist_alive = False
        else:
            pass
        if self.mode == "Playlist":
            self.playlist_open = True
        if self.mode != "Playlist":
            self.playlist_open = False
        if self.playlist_alive:
            if self.playlist_open:
                self.playlist_button['text'] = 'Delete Playlist'
            else:
                self.playlist_button['text'] = 'Open Playlist'
        if self.playlist_open:
            self.add_to_playlist_button['text'] = 'Delete From Playlist'

        self.playlist_button.pack(expand=True)
        self.add_to_playlist_button.pack(expand=True)

    def create_playlist_wrapper(self):
        if self.playlist_alive:
            if not self.playlist_open:
                self.images_array.clear()
                self.mode = 'Playlist'
                query = '''SELECT * FROM Playlist INNER JOIN Main ON Main.SongID = Playlist.SongID INNER JOIN Songs ON 
                        Main.SongID = Songs.SongID INNER JOIN Albums ON Songs.AlbumID = Albums.AlbumID INNER JOIN Artists 
                        ON Albums.ArtistID = Artists.ArtistID;'''
                self.cur.execute(query)
                self.playlist_open = True

                result = self.cur.fetchall()
                query = '''SELECT COUNT(Songs.SongID) FROM Playlist INNER JOIN Main ON Main.SongID = Playlist.SongID 
                INNER JOIN Songs ON Main.SongID = Songs.SongID INNER JOIN Albums ON Songs.AlbumID = Albums.AlbumID INNER 
                JOIN Artists ON Albums.ArtistID = Artists.ArtistID WHERE Artists.ArtistName LIKE 'Radiohead';'''
                self.cur.execute(query)
                radiohead_songs = self.cur.fetchall()[0][0]

                query = '''SELECT COUNT(Songs.SongID) FROM Playlist INNER JOIN Main ON Main.SongID = Playlist.SongID 
                                    INNER JOIN Songs ON Main.SongID = Songs.SongID INNER JOIN Albums ON Songs.AlbumID = 
                Albums.AlbumID INNER JOIN Artists ON Albums.ArtistID = Artists.ArtistID WHERE Songs.SongName LIKE '______';'''
                self.cur.execute(query)
                six_word_songs_titles = self.cur.fetchall()[0][0]
                self.entry_tree_constructor(self.column_names_playlist_mode)
                self.title(
                    "{} Radiohead songs. {} songs with 6-word titles".format(radiohead_songs, six_word_songs_titles))
                self.playlist_button['text'] = "Delete Playlist"
                self.counter = 0
                for row in result:
                    img_name = "album_icons/" + row[11] + ".gif"
                    img_name = img_name.replace(" ", "")
                    time_str = str(row[4]) + ":"
                    if row[5] < 10:
                        time_str = time_str + "0"
                    time_str = time_str + str(row[5])
                    if os.path.isfile(img_name):
                        self.images_array.append(tk.PhotoImage(file=img_name))
                    else:
                        self.images_array.append(tk.PhotoImage(file="pablo.gif"))
                    self.table_treeview.insert(parent='', index='end', iid=row[0], text="",
                                               image=self.images_array[self.counter],
                                               values=(
                                                   row[3], row[11], time_str, row[16], row[13], row[17], row[12],
                                                   row[6],
                                                   row[7]))
                    self.counter += 1

            else:
                query = '''DROP TABLE Playlist;'''
                self.cur.execute(query)
                self.playlist_alive = False
                self.playlist_open = False
                self.playlist_button['text'] = "Create Playlist"
                self.artist_view_entry()
        else:
            self.playlist_alive = True
            self.playlist_button['text'] = "Open Playlist"
            query = "CREATE TABLE Playlist ( SongID int, PRIMARY KEY (SongID) );"
            self.cur.execute(query)

    def add_song_to_playlist(self):
        if not self.playlist_alive:
            pass
        else:
            if self.playlist_open:
                curr_item = self.table_treeview.focus()
                query = "DELETE FROM Playlist WHERE SongID = {};".format(curr_item)
                self.cur.execute(query)

                self.images_array.clear()
                self.mode = 'Playlist'
                query = '''SELECT * FROM Playlist INNER JOIN Main ON Main.SongID = Playlist.SongID INNER JOIN Songs ON 
                    Main.SongID = Songs.SongID INNER JOIN Albums ON Songs.AlbumID = Albums.AlbumID INNER JOIN Artists 
                    ON Albums.ArtistID = Artists.ArtistID;'''
                self.cur.execute(query)

                self.playlist_open = True

                result = self.cur.fetchall()
                query = '''SELECT COUNT(Songs.SongID) FROM Playlist INNER JOIN Main ON Main.SongID = Playlist.SongID 
                                                INNER JOIN Songs ON Main.SongID = Songs.SongID INNER JOIN Albums ON Songs.AlbumID = Albums.AlbumID INNER
                                                 JOIN Artists ON Albums.ArtistID = Artists.ArtistID WHERE Artists.ArtistName LIKE 'Radiohead';'''
                self.cur.execute(query)
                radiohead_songs = self.cur.fetchall()[0][0]

                query = '''SELECT COUNT(Songs.SongID) FROM Playlist INNER JOIN Main ON Main.SongID = Playlist.SongID 
                                                            INNER JOIN Songs ON Main.SongID = Songs.SongID INNER JOIN Albums ON Songs.AlbumID = 
                                                            Albums.AlbumID INNER JOIN Artists ON Albums.ArtistID = Artists.ArtistID WHERE Songs.SongName LIKE '______';'''
                self.cur.execute(query)
                six_word_songs_titles = self.cur.fetchall()[0][0]
                self.entry_tree_constructor(self.column_names_playlist_mode)
                self.title(
                    "{} Radiohead songs. {} songs with 6-word titles".format(radiohead_songs, six_word_songs_titles))
                self.playlist_button['text'] = "Delete Playlist"
                self.counter = 0
                for row in result:
                    img_name = "album_icons/" + row[11] + ".gif"
                    img_name = img_name.replace(" ", "")
                    time_str = str(row[4]) + ":"
                    if row[5] < 10:
                        time_str = time_str + "0"
                    time_str = time_str + str(row[5])
                    if os.path.isfile(img_name):
                        self.images_array.append(tk.PhotoImage(file=img_name))
                    else:
                        self.images_array.append(tk.PhotoImage(file="pablo.gif"))
                    self.table_treeview.insert(parent='', index='end', iid=row[0], text="",
                                               image=self.images_array[self.counter],
                                               values=(
                                                   row[3], row[11], time_str, row[16], row[13], row[17], row[12],
                                                   row[6],
                                                   row[7]))
                    self.counter += 1
            else:
                if self.mode == "Search":
                    song_id = int(self.table_treeview.focus()) + 1
                    query = "INSERT INTO Playlist VALUES ({});".format(song_id)
                    self.cur.execute(query)

    def add_entry(self, copies):
        for i in self.table_treeview.get_children():
            self.table_treeview.delete(i)

        for i in range(copies):
            self.table_treeview.insert(parent='', index='end', iid=i, text=0, image=self._img,
                                       values=(
                                           'Creep', 'Pablo Honey', 'Radiohead', '1992', 'Doomer Music',
                                           'EMI records', '3:08'))

    def add_other_entry(self, copies):
        self.mode = 'Artist'
        for i in self.table_treeview.get_children():
            self.table_treeview.delete(i)

        self.table_treeview['columns'] = tuple(self.column_names_playlist_mode)

        self.table_treeview.column("#0", width=30, stretch=tk.NO)
        self.table_width = int(1260 / len(self.column_names_playlist_mode))
        for name in self.column_names_playlist_mode:
            self.table_treeview.column(name, anchor=tk.CENTER, width=self.table_width)

        self.table_treeview.heading("#0", text="", anchor=tk.CENTER)
        for name in self.column_names_playlist_mode:
            self.table_treeview.heading(name, text=name, anchor=tk.CENTER)

        for i in self.table_treeview.get_children():
            self.table_treeview.delete(i)

        for i in range(copies):
            self.table_treeview.insert(parent='', index='end', iid=i, text="", image=self._img,
                                       values=(
                                           'You', 'Pablo Honey', 'Radiohead', '1992', 'Doomer Music',
                                           'EMI records', '3:29'))


def main():
    app = App()
    app.mainloop()


if __name__ == '__main__':
    main()
