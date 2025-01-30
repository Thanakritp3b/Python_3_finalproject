from flask import Flask, request, jsonify
from flask_cors import CORS
import networkx as nx
from PIL import Image, ImageDraw
import numpy as np
import random
from io import BytesIO
import base64

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

def parse_maze_text(maze_text):
    lines = maze_text.strip().split('\n')
    maze = []
    for line in lines:
        row = []
        for char in line.strip():
            if char in ['0', ' ', '*']:  
                row.append(0)
            elif char in ['1', '#']:  
                row.append(1)
            elif char == 'S': 
                row.append('S')
            elif char == 'E':  
                row.append('E')
        maze.append(row)
    return np.array(maze, dtype=object)  

def maze_to_text(maze, use_symbols=False):
    height, width = maze.shape
    lines = []
    for y in range(height):
        line = ""
        for x in range(width):
            cell = maze[y][x]
            if cell == 1:
                line += '#' if use_symbols else '1'
            elif cell == 0:
                line += '*' if use_symbols else '0'
            else:  # 'S' or 'E'
                line += str(cell)
        lines.append(line)
    return '\n'.join(lines)

def create_random_maze(width, height):
 
    maze = np.full((height, width), 1, dtype=object)
    
    def carve_path(x, y):
        maze[y][x] = 0
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if (0 <= new_x < width and 0 <= new_y < height and 
                maze[new_y][new_x] == 1):
                maze[y + dy//2][x + dx//2] = 0
                carve_path(new_x, new_y)
    
    carve_path(1, 1)
    
    maze[1][1] = 'S'
    maze[height-2][width-2] = 'E'
    return maze

def maze_to_graph(maze):
    G = nx.Graph()
    height, width = len(maze), len(maze[0])
    
    for y in range(height):
        for x in range(width):
            if maze[y][x] != 1: 
                pos = (x, y)
           
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    new_x, new_y = x + dx, y + dy
                    if (0 <= new_x < width and 0 <= new_y < height and 
                        maze[new_y][new_x] != 1):
                        G.add_edge((x, y), (new_x, new_y))
    return G

def find_path(maze, algorithm='bfs'):

    G = maze_to_graph(maze)
    start = None
    end = None
 
    for y in range(len(maze)):
        for x in range(len(maze[0])):
            if maze[y][x] == 'S':
                start = (x, y)
            elif maze[y][x] == 'E':
                end = (x, y)
    
    try:
        if algorithm == 'bfs':
            path = nx.shortest_path(G, start, end)
        else:  # DFS
            paths = list(nx.all_simple_paths(G, start, end))
            path = paths[0] if paths else None
        return path
    except nx.NetworkXNoPath:
        return None

def maze_to_image(maze, path=None):
 
    height, width = len(maze), len(maze[0])
    cell_size = 30 
    img = Image.new('RGB', (width * cell_size, height * cell_size), 'white')
    draw = ImageDraw.Draw(img)
    
    
    for y in range(height):
        for x in range(width):
            cell = maze[y][x]
            rect = [x*cell_size, y*cell_size, (x+1)*cell_size, (y+1)*cell_size]
            
            if cell == 1:  
                draw.rectangle(rect, fill='black')
            elif cell == 'S': 
                draw.rectangle(rect, fill='green')
                draw.text((x*cell_size + 5, y*cell_size + 5), 'S', fill='white')
            elif cell == 'E':  
                draw.rectangle(rect, fill='red')
                draw.text((x*cell_size + 5, y*cell_size + 5), 'E', fill='white')
    
    if path:
        for i in range(len(path)-1):
            x1, y1 = path[i]
            x2, y2 = path[i+1]
            draw.line([(x1*cell_size + cell_size//2, y1*cell_size + cell_size//2),
                      (x2*cell_size + cell_size//2, y2*cell_size + cell_size//2)],
                     fill='blue', width=4)
    

    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

@app.route('/generate', methods=['POST'])
def generate_maze():
    data = request.get_json()
    width = data.get('width', 15)
    height = data.get('height', 15)
    use_symbols = data.get('useSymbols', False)
    
    maze = create_random_maze(width, height)
    maze_text = maze_to_text(maze, use_symbols)
    image = maze_to_image(maze)
    
    return jsonify({
        'maze': maze.tolist(),
        'mazeText': maze_text,
        'image': image
    })

@app.route('/solve', methods=['POST'])
def solve_maze():
    data = request.get_json()
    maze_text = data.get('mazeText', '')
    algorithm = data.get('algorithm', 'bfs')
    
    try:
        maze = parse_maze_text(maze_text)
        path = find_path(maze, algorithm)
        
        if path is None:
            return jsonify({'error': 'No solution found'}), 400
            
        image = maze_to_image(maze, path)
        return jsonify({
            'path': path,
            'image': image
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)