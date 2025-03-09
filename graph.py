from graphviz import Digraph

def create_diagram():
    dot = Digraph(format='png')
    
    # Define nodes
    dot.node('A', 'Webcam Input\n(OpenCV Capture)', shape='box')
    dot.node('B', 'Hand Detection\n(MediaPipe)', shape='box')
    dot.node('C', 'Mouse Control\n(AutoPy)', shape='box')
    dot.node('D', 'Frame Processing\n(OpenCV)', shape='box')
    dot.node('E', 'Gesture Mapping\n(Custom Logic)', shape='box')
    dot.node('F', 'System Output\n(Cursor Movement,\nClicks, Scrolls)', shape='box')
    
    # Define edges
    dot.edge('A', 'B')
    dot.edge('B', 'C')
    dot.edge('A', 'D')
    dot.edge('B', 'E')
    dot.edge('C', 'F')
    
    # Render and save the file
    dot.render('hand_tracking_diagram', view=True)
    
create_diagram()
