import os
import time
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

log_file_path = 'logfile.log'
log_buffer_size = 10


# def read_last_n_lines(file_path, n):
#     with open(file_path, 'r') as file:
#         lines = file.readlines()
#         return lines[-n:]

def read_last_n_lines(file_path, n):
    lines = []
    BLOCK_SIZE = 1024

    with open(file_path, 'r') as f:
        f.seek(0, 2)
        block_end_byte = f.tell()
        lines_to_go = n
        block_number = -1

        while lines_to_go > 0 and block_end_byte > 0:
            if block_end_byte - BLOCK_SIZE > 0:
                f.seek(block_number * BLOCK_SIZE, 2)
                block = f.read(BLOCK_SIZE)
            else:
                f.seek(0, 0)
                block = f.read(block_end_byte)

            lines_in_block = block.count('\n')
            if lines_in_block > lines_to_go:
                lines.extend(block.splitlines()[-lines_to_go:])
                break
            else:
                lines.extend(block.splitlines())
                lines_to_go -= lines_in_block
                block_end_byte -= BLOCK_SIZE
                block_number -= 1

    return lines


@app.route('/log')
def log():
    lines = read_last_n_lines(log_file_path, log_buffer_size)
    return render_template('log.html', lines=lines)


@socketio.on('connect', namespace='/log')
def handle_connect():
    print('Client connected')


@socketio.on('disconnect', namespace='/log')
def handle_disconnect():
    print('Client disconnected')


def tail_file():
    with open(log_file_path, 'r') as file:
        file.seek(0, os.SEEK_END)
        while True:
            print("In the while loop")
            current_position = file.tell()
            print(current_position)
            line = file.readline()
            if not line:
                time.sleep(1)
                file.seek(current_position)
            else:
                print(line)
                socketio.emit('log_update', {'line': line}, namespace='/log')  # Add namespace='/log'


if __name__ == '__main__':
    socketio.start_background_task(target=tail_file)
    socketio.run(app, debug=True, use_reloader=False, use_debugger=False, allow_unsafe_werkzeug=True)





