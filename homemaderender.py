import pygame
import pygame.gfxdraw
import math, os, sys

# This is a project that I am starting because I want to learn how to translate 3d objects onto a 2d screen

'''
    INFO:
   -Welcome to Brennan McMicking's homemade 3d rendering engine.
   -This program is simply an application of the things that I have learned in Math 110 and Computer Science 111.
   -I chose to use Python instead of C because Python already has a handy-dandy library called Pygame that gives me the PERFECT amount
    of functionality that I need without giving me any crutches (I can render 2d shapes, but not 3d ones, so I need to find out how to do that
    myself)
   -As of now, this program is not perfect. There is still fisheye distortion on the camera (which a quick google search could probably fix,
    but I'd rather try to fix on my own)
    There is also the problem of clipping the polygons as they reach the edge of the screen, because if a vertex goes too far off then it
    will fail to render the face entirely (which can also be fixed, but the solution makes the entire rendering process magnitudes more
    complicated. From what I've seen, it involves the cross product, which is not hard to implement at all, but the problem is knowing how
    to use it)
'''

# first we will set variables for all the colors we will use 
# we'll just hard-code them, cause why not?
black = (0, 0, 0)
sky = (128,128,255)

white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
orange = (255,128,0)
yellow = (255,255,0)

colors = [white, red, green, blue, orange, yellow]

print("Hello, World!")

# Initialise pygame
pygame.init()

# The size of the screen
width = 800
height = 600

# The field of view
fov = 110

# The center of the screen
cx = width//2
cy = height//2

# Tell the OS to centre the window on the screen
os.environ['SDL_VIDEO_CENTERED'] = '1'

# Set the window title
pygame.display.set_caption('Homemade Render')

# Make a window
screen = pygame.display.set_mode((width,height))

# Get our clock function
clock = pygame.time.Clock()

# Set up the mouse
pygame.event.get()
pygame.mouse.get_rel()
pygame.mouse.set_visible(0)
pygame.event.set_grab(1)

# Font
font = pygame.font.SysFont("Arial", 10)


# Load the Minecraft grass texture (currently broken)
texture = pygame.image.load('grass.png').convert()


# This mess defines where every face on a cube is, namely, it names 4 positions that all exist in 2d space and call them a "polygon"
# This allows for different shapes to eventually be added other than normal cubes
polyf = (-1, 1, -1), (1, 1, -1), (1, -1, -1), (-1, -1, -1)
polya = (-1, 1, 1), (1, 1, 1), (1, -1, 1), (-1, -1, 1)
polyl = (-1, 1, -1), (-1, 1, 1), (-1, -1, 1), (-1, -1, -1)
polyr = (1, 1, 1), (1, 1, -1), (1, -1, -1), (1, -1, 1)
polyt = (-1, 1, -1), (-1, 1, 1), (1, 1, 1), (1, 1, -1)
polyb = (-1, -1, -1), (-1, -1, 1), (1, -1, 1), (1, -1, -1)
# We define a cube as being a set of these 6 faces
cube_f = [polyf, polya, polyl, polyr, polyt, polyb]


# Given a vector [x, y], rotate it around theta (I got this function from my math 110 class, aka Linear Algebra for Engineers)
def T_by_theta(x, y, theta):
    sin_t = math.sin(theta)
    cos_t = math.cos(theta)
    x_out = x*cos_t - y*sin_t
    y_out = x*sin_t + y*cos_t
    return (x_out, y_out)

# return the dot product of v, w, provided that they both have the same length
def dot(v, w):
    d = 0
    if len(v) == len(w):
        for x in range(len(v)):
            d += v[x]*w[x]
    
    return d

# return the magnitude of v
def mag(v):
    return math.sqrt(dot(v, v))

# the sigmoid function is a normalization function that takes an input x and returns a value between 0 and 1
# as x goes to -infinity, sigmoid(x) goes to 0. As x goes to +infinity, sigmoid(x) goes to 1
def sigmoid(x):
    return 1/(1+math.exp(-x))


# given a color, level of the nearest light, and the distance to the nearest light, return the "dimmed" color
def dim_color(color, level, d):
    r, g, b = color
    
    f = sigmoid(level/d)
    # f = level/d
    
    # print(f)
    
    return (r*f, g*f, b*f)


# Reproduceable cube class for S C A L E A B I L I T Y
class Cube:
    def __init__(self, pos=[0, 0, 1]):
        self.pos = pos
        

# Reproduceable light class, also for S C A L E A B I L I T Y
class Light:
    def __init__(self, level=10, pos=[0, 0, 1]):
        self.level = level
        self.pos = pos
    

# Class for the camera
class Camera:
    def __init__(self, pos=[0,0,-3], angle=[0,0]):
        self.pos = pos
        self.angle = angle
        
    def on_game_frame(self, time, key):
    
        # If W is pressed, move the camera in the Z direction by the cosine of it's angle in the y axis
        # Also move in the X direction by the sine of it's angle in the y axis
        # Draw a diagram if you are unsure of how this works. 
    
        if key[pygame.K_w]:
            camera.pos[2] += 0.01*time*math.cos(camera.angle[1])
            camera.pos[0] += 0.01*time*math.sin(camera.angle[1])
    
        if key[pygame.K_s]:
            camera.pos[2] -= 0.01*time*math.cos(camera.angle[1])
            camera.pos[0] -= 0.01*time*math.sin(camera.angle[1])
        
        if key[pygame.K_a]:
            camera.pos[0] -= 0.01*time*math.cos(camera.angle[1])
            camera.pos[2] += 0.01*time*math.sin(camera.angle[1])
            
        if key[pygame.K_d]:
            camera.pos[0] += 0.01*time*math.cos(camera.angle[1])
            camera.pos[2] -= 0.01*time*math.sin(camera.angle[1])
        
        # Move the camera up
        if key[pygame.K_e]:
            camera.pos[1] += 0.01*time
        
        # Move the camera down
        if key[pygame.K_q]:
            camera.pos[1] -= 0.01*time
        
        # Turn the camera to the right
        if key[pygame.K_RIGHT]:
            camera.angle[1] += 0.01*time

        # Turn left
        if key[pygame.K_LEFT]:
            camera.angle[1] -= 0.01*time
            
        # Tilt upwards
        if key[pygame.K_UP]:
            camera.angle[0] -= 0.01*time

        # Tilt downwards
        if key[pygame.K_DOWN]:
            camera.angle[0] += 0.01*time
    

cont = True

# Define all cubes in the game. This is not so practical as it must be handwritten, but loops can be made to automate this
cubes = [Cube(), Cube([4,0,1]), Cube([4,2,1]), Cube([4,0,-1])]

# Define all lights in the game
lights = [Light(level=5)]

# Other cube stuff
# cubes = [Cube(), Cube((3, 2, 1))]


# Set the camera
camera = Camera()


while cont:
    # fill the screen with sky color
    screen.fill(sky)
    
    # time will be used to make sure that no matter how long it takes to render a frame, all the user inputs will happen at the same rate
    time = clock.tick()
    
    # We can also handle keyboard input in events but it only allows one key input per frame, whereas our solution below will allow
    # all different keys to be read on the same frame
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            # If the user presses the X in the game window, close the game.
            cont = False
            sys.exit()
        if event.type == pygame.MOUSEMOTION:
            # Get the amount of pixels that the mouse moved since last call to event.get()
            mx,my = event.rel
            camera.angle[1] += mx*0.001*time
            camera.angle[0] += my*0.001*time
    
    # key.get_pressed() returns a list of all integers, either 0 or 1, where each key is either pressed or not pressed
    key = pygame.key.get_pressed()
    
    camera.on_game_frame(time, key)
    
    # If escape is pressed, exit
    if key[pygame.K_ESCAPE]:
        cont = False
        sys.exit()
    
    
    
    # Create a list, one with the x,y screen coordinates of all the faces embedded as lists inside the list
    # Another list will hold the absolute magnitude of the distance from the Face to the Camera
    # The final list will hold the color value of the face after it has been modified considering the nearest light
    faces = []
    faces_dist = []
    color_out = []
    for cube in cubes:
        # We must make the camera the origin, and translate the face around it
        x = cube.pos[0] - camera.pos[0]
        y = cube.pos[1] - camera.pos[1]
        z = cube.pos[2] - camera.pos[2]
        
        
        i = 0
        # if I were to make cube_f an attribute of the cube, then it would be possible to have polygons other than cubes, and the list of x,y,z
        # coordinates of each vertex would be available under cube.vertices or something like that
        # Just a note for later
        for poly in cube_f:
            # Make a list of coords within each face
            face = []
            avg_pos = [0, 0, 0]
            # print(poly)
            
            
            # WARNING: for this for loop, I ended making way more variables than I needed because when I was writing it originally,
            # it took a lot of work to make it behave how I wanted it to and now I'm too scared to try to do any cleanup just in case
            # it stops working
            # Essentially, this next bit is a hot mess but it ain't broke so I ain't gonna fix it
            for item in poly:
                # print(item)
                # for every (x, y, z) in poly
                
                # if x, y, z is the full cube's position, then the position of the current vertex is calculated as:
                px = x + item[0]
                py = y + item[1]
                pz = z + item[2]
                
                # store these for later, cause we're gonna modify them!
                dx = px
                dy = py
                dz = pz
                
                # store the z value again.
                
                fz = pz
                
                # d is the absolute distance from px, py, pz to the camera (this will be used to calculate which faces are going to
                # be rendered first
                d = mag([px, py, pz])
                
                
                # Translate the vector from the camera to the point in only the 
                # x,z plane around the angle of the camera's rotation in the y plane ( aka the camera's horizontal rotation )
                px, pz = T_by_theta(px, pz, camera.angle[1]) 
                dz = pz
                py, pz = T_by_theta(py, pz, camera.angle[0]) 
                
                fz -= dz*math.sin(camera.angle[1])
                
                
                if dz > 0:
                    
                    fx = px*fov/pz+cx
                    fy = py*fov/pz+cy
                
                    face.append([fx, fy])
                    avg_pos[0] += dx
                    avg_pos[1] += dy
                    avg_pos[2] += dz
            
            # d is the absolute distance from the center of the face to the camera (this will be used to calculate which faces are going to
            # be rendered first)
            d = mag([avg_pos[0], avg_pos[1], avg_pos[2]])
            
            # right now there is only one light and it is locked on the camera, but this loop and stuff allows for
            # S C A L E A B I L I T Y
            nx = lights[0].pos[0]
            ny = lights[0].pos[1]
            nz = lights[0].pos[2]
            nearest = lights[0]
            
            for light in lights:
                lx = avg_pos[0] - light.pos[0]
                ly = avg_pos[0] - light.pos[0]
                lz = avg_pos[0] - light.pos[0]
                
                # starting with the first light, loop through all the lights and find the closest one.
                # once found, calculate how much it will "light up" the cube (see c = dim(...) below)
                
                if mag((lx, ly, lz)) < mag((nx, ny, nz)):
                    nx = lx
                    ny = ly
                    nz = lz
                    nearest = light
                
                
            # We now know the nearest light. The face's color is going to be dimmed depending on how close
            # the light is and the level of the light
            c = dim_color(colors[i], nearest.level, mag(nearest.pos))
            
            i += 1
            # d_font = font.render("d = " + str(mag(nearest.pos)), False, white)
            # pos_font = font.render(str(nearest.pos), False, white)
            
            # print(c)
            
            # save the distance of the face in a list
            # save the actual 2d screen coordinates of the face in a list
            # save the color of the face in a list
            faces_dist += [d]
            faces += [face]
            color_out += [c]
            
                
    

    # print(faces)
    
    
    # d_font = font.render("d = " + str(d), False, white)
    pos_font = font.render(str(cube.pos), False, white)
    angle_font = font.render(str(camera.angle), False, white)
    
    # Now that we have calculated all of the faces, we must order them based on their distance to the camera from back to front, so that we will render
    # the furthest faces first
    face_order = sorted(range(len(faces)), key=lambda i: faces_dist[i], reverse=True)
    

    for i in face_order:
        
        # try to render each face on the "screen" object. if it fails, don't worry! it's better to just push on to the next frame
        # than get caught up in trying to fix anything
        try:
            pygame.draw.polygon(screen, color_out[i], faces[i])
            # pygame.gfxdraw.textured_polygon(screen, faces[i], texture, 0, 0)
        except:
            # print("Failed: " + str(faces[i]))
            continue
        
        
    
    
    
    # screen.blit(d_font, [10, 10])
    # screen.blit(pos_font, [10, 20])
    screen.blit(angle_font, [10, 30])
    
    
    # Jut lock the only light onto the camera for now so that you can see it do it's magic as the camera moves toward and away from the cubes
    lights[0].pos = camera.pos
    
    
    # Now we flip the screen object onto the actual window
    pygame.display.flip()