import pygame
import pygame.gfxdraw
import math
import os
import sys
from noise import snoise2

# pip install noise
# pip install pygame

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

'''
TODO:
    -Fix lighting
    -Increase the precision of the clipping algorithm so that
     it checks to see if the line between each point is on the screen at all
    -Maybe just draw faces by drawing lines, and clip each line at the edge of the screen or smth,
     instead of drawing each face as a polygon
    -Create chunks and build each chunk into "meshes"
'''

# first we will set variables for all the colors we will use
# we'll just hard-code them, cause why not?
black = (0, 0, 0)
sky = (128, 128, 255)

white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
orange = (255, 128, 0)
yellow = (255, 255, 0)

colors = [white, red, green, blue, orange, yellow]

seed = 12345678

# Initialise pygame
pygame.init()

# The size of the screen
width = 800
height = 600

# The field of view
fov = 200

# The center of the screen
cx = width//2
cy = height//2

# Tell the OS to centre the window on the screen
os.environ['SDL_VIDEO_CENTERED'] = '1'

# Set the window title
pygame.display.set_caption('Homemade Render')

# Make a window
screen = pygame.display.set_mode((width, height))

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
# texture = pygame.image.load('grass.png').convert()

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

# just returns whether or not any point in the face is on the screen or not


def face_is_on_screen(face):
    for point in face:
        if point_is_on_screen(point):
            return True

    return False


# just returns whether the point is on the screen or not
def point_is_on_screen(point):
    if point[0] > width or point[0] < 0:
        return False
    if point[1] > height or point[1] < 0:
        return False

    return True


def clip_point(cur, prev):
    new_point = []
    if cur[0] < 0:
        alpha = cur[0] - prev[0]
        gamma = cur[1] - prev[1]
        rho = 0 - prev[0]
        hi = prev[1]

        if alpha == 0:
            new_point = [0, height]
        else:
            new_point = [0, int(hi + rho * gamma / alpha)]

    elif cur[0] > width:
        alpha = prev[0] - cur[0]
        gamma = prev[1] - cur[1]
        rho = width - prev[0]
        hi = prev[1]

        if alpha == 0:
            new_point = [width, height]
        else:
            new_point = [width, int(hi + rho * gamma / alpha)]

    if cur[1] < 0:
        alpha = cur[1] - prev[1]
        gamma = cur[0] - prev[0]
        rho = 0 - prev[1]
        hi = prev[0]

        if alpha == 0:
            new_point = [width, 0]
        else:
            new_point = [int(hi + rho * gamma / alpha), 0]

    elif cur[1] > height:
        alpha = cur[1] - prev[1]
        gamma = cur[0] - prev[0]
        rho = height - prev[1]
        hi = prev[0]

        if alpha == 0:
            new_point = [width, height]
        else:
            new_point = [int(hi + rho * gamma / alpha), height]

    return new_point

# clip takes a face and fixes every point that is not on the screen to the edge of the screen


def clip(face):
    new_face = []
    '''
    There are 3 cases for each point in the face:
        - both of the adjacent points are on the screen
            -need to create a point at both point intersection points 
            (aka we need to do the calculation twice)
        - only one of the adjacent points is on the screen
            (aka we only need to do the calculation once)
        - neither of the adjacent points are on the screen
            (we can just pretend the point doesn't exist)
    '''

    clipped = False

    for i in range(len(face)):
        cur = face[i]
        if not point_is_on_screen(cur):
            clipped = True
            # print("face not on screen: " + str(face))
            new_point = []
            j = i + 1
            if i == len(face) - 1:
                j = 0

            middle_point = None
            if face[i][0] > width and face[i][1] > height:
                middle_point = [width, height]
            if face[i][0] > width and face[i][1] < 0:
                middle_point = [width, 0]
            if face[i][0] < 0 and face[i][1] > height:
                middle_point = [0, height]
            if face[i][0] < 0 and face[i][1] < 0:
                middle_point = [0, 0]

            if not point_is_on_screen(face[j]) and not point_is_on_screen(face[i - 1]):
                # neither adjacent point is on the screen
                # so we ignore this point altogether
                if middle_point is not None:
                    new_face.append(middle_point)

            elif point_is_on_screen(face[j]) and point_is_on_screen(face[i - 1]):
                # both adjacent are on the screen
                new1 = clip_point(cur, face[i-1])
                while not point_is_on_screen(new1):
                    new1 = clip_point(new1, face[i-1])

                new2 = clip_point(cur, face[j])
                while not point_is_on_screen(new2):
                    new2 = clip_point(new2, face[j])
                # clipped = True
                #print("clipped " + str(cur) + " to " + str(new1) + ", " + str(new2))
                new_face.append(new1)

                if middle_point is not None:
                    new_face.append(middle_point)

                new_face.append(new2)

                # print("double clipped point " + str(cur))
            else:
                # 1 adjacent point is on the screen
                if point_is_on_screen(face[j]):
                    if middle_point is not None:
                        # print("adding middle point")
                        # print(f"middle point is: {middle_point}")
                        new_face.append(middle_point)
                    new_face.append(clip_point(cur, face[j]))
                else:
                    new_face.append(clip_point(cur, face[i-1]))
                    if middle_point is not None:
                        new_face.append(middle_point)

                # new_face.append(clip_point(cur, face[i-1]))
                # new_face.append(clip_point(cur, face[j]))

        else:
            new_face.append(cur)

    # if clipped:
    #     print(str(new_face))

    return new_face


# given a color, level of the nearest light, and the distance to the nearest light, return the "dimmed" color
def dim_color(color, level, d):

    r, g, b = color
    '''
    if d != 0:
        f = sigmoid(level/d)
    else:
        f = 1
    '''

    f = sigmoid((level)/d)

    # f = level/d
    # print(f)
    r_out = r*f
    g_out = g*f
    b_out = b*f

    # print((r_out, g_out, b_out))

    return (r_out, g_out, b_out)


class Face:
    def __init__(self, pos=[0, 0, 0]):
        self.pos = pos


class Chunk:
    def __init__(self, pos=[0, 0, 0]):
        self.pos = pos
        for x in range(16):
            for z in range(16):
                y = int(snoise2(x, z, seed))
                print(y)
                # self.blocks[x][y][z] = Cube([x, y, z])

    def build_mesh(self):
        # go thru every block in the chunk and find the faces that have air next to them. add them to the mesh and return that mesh
        return 1

    def get_cubes(self):
        return self.blocks


class Cube:
    # This mess defines where every face on a cube is, namely, it names 4 positions that all exist in 2d space and call them a "polygon"
    # This allows for different shapes to eventually be added other than normal cubes
    polyf = (-1, 1, -1), (1, 1, -1), (1, -1, -1), (-1, -1, -1)
    polya = (-1, 1, 1),  (1, 1, 1),  (1, -1, 1),  (-1, -1, 1)
    polyl = (-1, -1, 1), (-1, 1, 1), (-1, 1, -1), (-1, -1, -1)
    polyr = (1, -1, 1), (1, 1, 1), (1, 1, -1), (1, -1, -1)
    polyt = (-1, 1, 1), (1, 1, 1), (1, 1, -1), (-1, 1, -1)
    polyb = (-1, -1, 1), (1, -1, 1), (1, -1, -1), (-1, -1, -1)
    # We define a cube as being a set of these 6 faces
    cube_f = [polyf, polya, polyl, polyr, polyt, polyb]

    def __init__(self, pos=[0, 0, 1]):
        self.pos = pos


# Reproduceable light class, also for S C A L E A B I L I T Y
class Light:
    def __init__(self, level=10, pos=[0, 0, 1]):
        self.level = level
        self.pos = pos


# Class for the camera
class Camera:
    def __init__(self, pos=[0, 0, -3], angle=[0, 0]):
        self.pos = pos
        self.angle = angle

    def on_game_frame(self, time, key, mouse):
        mx, my = mouse

        self.angle[1] += mx*0.001*time
        self.angle[0] += my*0.001*time

        # If W is pressed, move the camera in the Z direction by the cosine of it's angle in the y axis
        # Also move in the X direction by the sine of it's angle in the y axis
        # Draw a diagram if you are unsure of how this works.

        if key[pygame.K_w]:
            self.pos[2] += 0.01*time*math.cos(self.angle[1])
            self.pos[0] += 0.01*time*math.sin(self.angle[1])

        if key[pygame.K_s]:
            self.pos[2] -= 0.01*time*math.cos(self.angle[1])
            self.pos[0] -= 0.01*time*math.sin(self.angle[1])

        if key[pygame.K_a]:
            self.pos[0] -= 0.01*time*math.cos(self.angle[1])
            self.pos[2] += 0.01*time*math.sin(self.angle[1])

        if key[pygame.K_d]:
            self.pos[0] += 0.01*time*math.cos(self.angle[1])
            self.pos[2] -= 0.01*time*math.sin(self.angle[1])

        # Move the camera up
        if key[pygame.K_e]:
            self.pos[1] += 0.01*time

        # Move the camera down
        if key[pygame.K_q]:
            self.pos[1] -= 0.01*time

        # Turn the camera to the right
        if key[pygame.K_RIGHT]:
            self.angle[1] += 0.01*time

        # Turn left
        if key[pygame.K_LEFT]:
            self.angle[1] -= 0.01*time

        # Tilt upwards
        if key[pygame.K_UP]:
            self.angle[0] -= 0.01*time

        # Tilt downwards
        if key[pygame.K_DOWN]:
            self.angle[0] += 0.01*time

        if self.angle[0] < -1:
            self.angle[0] = -1

        if self.angle[0] > 1:
            self.angle[0] = 1


cont = True

# Define all cubes in the game. This is not so practical as it must be handwritten, but loops can be made to automate this
# cubes = [Cube(), Cube([4,0,1]), Cube([4,2,1]), Cube([4,0,-1])]

# cubes = []

lighting = False

'''
for y in range(0, 2, 2):
    for x in range(0, 100, 2):
        cubes += [Cube([x, 0, y])]

    for x in range(0, 100, 2):
        cubes += [Cube([y, 0, x])]
'''
# Define all lights in the game
lights = [Light(level=50)]

# Other cube stuff
# cubes = [Cube(), Cube((3, 2, 1))]

# chunk = Chunk()

# cubes = [Cube(), Cube((3, 0, 0))]
# cubes = [Cube(pos=[3*x, 0, 0]) for x in range(10)]

cubes = [Cube()]

# Set the camera
camera = Camera()

while cont:
    # fill the screen with sky color
    screen.fill(sky)

    # time will be used to make sure that no matter how long it takes to render a frame, all the user inputs will happen at the same rate
    time = clock.tick()
    mx, my = 0, 0
    # We can also handle keyboard input in events but it only allows one key input per frame, whereas our solution below will allow
    # all different keys to be read on the same frame
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            # If the user presses the X in the game window, close the game.
            cont = False
            sys.exit()
        if event.type == pygame.MOUSEMOTION:
            # Get the amount of pixels that the mouse moved since last call to event.get()
            mx, my = event.rel

    # key.get_pressed() returns a list of all integers, either 0 or 1, where each key is either pressed or not pressed
    key = pygame.key.get_pressed()

    camera.on_game_frame(time, key, (mx, my))

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
        for poly in cube.cube_f:
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
                # be rendered first)
                d = mag([px, py, pz])

                # Translate the vector from the camera to the point in only the
                # x,z plane around the angle of the camera's rotation in the y plane ( aka the camera's horizontal rotation )
                px, pz = T_by_theta(px, pz, camera.angle[1])

                py, pz = T_by_theta(py, pz, camera.angle[0])

                # fz -= dz*math.sin(camera.angle[1])
                print(f'pz: {pz}')
                if pz > -1:
                    '''
                    if pz < 0:
                        pz = -pz
                    '''
                    screen_x = px+cx
                    screen_y = py+cy

                    face.append([int(screen_x), int(screen_y)])
                    avg_pos[0] += dx
                    avg_pos[1] += dy
                    avg_pos[2] += dz

            # d is the absolute distance from the center of the face to the camera (this will be used to calculate which faces are going to
            # be rendered first)

            d = mag([avg_pos[0], avg_pos[1], avg_pos[2]])

            # d_font = font.render("d = " + str(mag(nearest.pos)), False, white)
            # pos_font = font.render(str(nearest.pos), False, white)

            # print(c)

            # save the distance of the face in a list
            # save the actual 2d screen coordinates of the face in a list
            # save the color of the face in a list
            if(face_is_on_screen(face)):
                face = clip(face)
                #print("added face: " + str(face))
                if lighting:
                    # also draw the lights on the screen

                    for light in lights:
                        # Translate the light around the camera
                        pos_x = light.pos[0] - camera.pos[0]
                        pos_y = light.pos[1] - camera.pos[1]
                        pos_z = light.pos[2] - camera.pos[2]

                        dist = mag((pos_x, pos_y, pos_z))

                        # Translate into 2d
                        pos_x, pos_z = T_by_theta(
                            pos_x, pos_z, camera.angle[1])
                        pos_y, pos_z = T_by_theta(
                            pos_y, pos_z, camera.angle[0])

                        if pos_z > 0:
                            pos_x = pos_x * fov / pos_z + cx
                            pos_y = pos_y * fov / pos_z + cy
                            faces += [[pos_x + 1, pos_y + 1], [pos_x + 1, pos_y - 1],
                                      [pos_x - 1, pos_y - 1], [pos_x - 1, pos_y + 1]]
                            faces_dist += [dist]
                            color_out += [white]

                    nx = avg_pos[0] - lights[0].pos[0]
                    ny = avg_pos[1] - lights[0].pos[1]
                    nz = avg_pos[2] - lights[0].pos[2]
                    nearest = lights[0]

                    for light in lights:
                        lx = avg_pos[0] - light.pos[0]
                        ly = avg_pos[1] - light.pos[1]
                        lz = avg_pos[2] - light.pos[2]

                        # starting with the first light, loop through all the lights and find the closest one.
                        # once found, calculate how much it will "light up" the cube (see c = dim(...) below)

                        if mag((lx, ly, lz)) < mag((nx, ny, nz)):
                            nx = lx
                            ny = ly
                            nz = lz
                            nearest = light

                    # We now know the nearest light. The face's color is going to be dimmed depending on how close
                    # the light is and the level of the light
                    c = dim_color(colors[i], nearest.level, mag((nx, ny, nz)))
                    color_out += [c]
                else:
                    color_out += [colors[i]]
                faces_dist += [d]
                faces += [face]

            i += 1

    # print(faces)

    # d_font = font.render("d = " + str(d), False, white)
    fps_font = font.render(str(int(clock.get_fps())), False, white)
    pos_font = font.render(str(cube.pos), False, white)
    angle_font = font.render(str(camera.angle), False, white)

    # Now that we have calculated all of the faces, we must order them based on their distance to the camera from back to front, so that we will render
    # the furthest faces first

    # print(range(len(faces)))
    try:
        face_order = sorted(range(len(faces)),
                            key=lambda i: faces_dist[i], reverse=True)
    except:
        continue
    else:
        for i in face_order:

            # print(color_out[i], faces[i])

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
    screen.blit(fps_font, [10, 20])
    screen.blit(angle_font, [10, 30])

    # Jut lock the only light onto the camera for now so that you can see it do it's magic as the camera moves toward and away from the cubes

    '''
    lights[0].pos[0] = camera.pos[0]
    lights[0].pos[1] = camera.pos[1]
    lights[0].pos[2] = camera.pos[2]
    '''

    # Now we flip the screen object onto the actual window
    pygame.display.flip()
