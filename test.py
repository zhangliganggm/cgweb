from __future__ import division
import OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image
import time, sys
import numpy as np


WIDTH = 400
HEIGHT = 300

def InitGL():
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45.0, float(WIDTH) / float(HEIGHT), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)


def DrawGLScene():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0, 0., -3)
    glutWireTeapot(1)
    glFlush()

def capture_screen():
    DrawGLScene()
    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    data = glReadPixels(0, 0, WIDTH, HEIGHT, GL_RGBA, GL_UNSIGNED_BYTE)
    image = Image.fromstring("RGBA", (WIDTH, HEIGHT), data)
    image.transpose(Image.FLIP_TOP_BOTTOM).show()

def capture_fbo(width=800, height=600):

    fbo = glGenFramebuffers(1)
    render_buf = glGenRenderbuffers(1)

    glBindRenderbuffer(GL_RENDERBUFFER, render_buf)

    glRenderbufferStorage(GL_RENDERBUFFER, GL_RGBA, width, height);
    glBindFramebuffer(GL_FRAMEBUFFER, fbo)
    glFramebufferRenderbuffer(GL_DRAW_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_RENDERBUFFER, render_buf);
    glBindFramebuffer(GL_DRAW_FRAMEBUFFER, fbo);

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(1, 1., -3)
    glScale(width / WIDTH, height / HEIGHT, 1)
    glutWireTeapot(1.0)
    glFlush()
    glReadBuffer(GL_COLOR_ATTACHMENT0);
    data = glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE)
    glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0);
    image = Image.fromstring("RGBA", (width, height), data)
    image.transpose(Image.FLIP_TOP_BOTTOM).show()

    glDeleteFramebuffers(1, [fbo]);
    glDeleteRenderbuffers(1, [render_buf]);


glutInit(sys.argv)
glutInitDisplayMode(GLUT_RGBA | GLUT_DEPTH)
glutInitWindowSize(WIDTH, HEIGHT)
window = glutCreateWindow("")
glutDisplayFunc(DrawGLScene)
InitGL()
DrawGLScene()
capture_screen()
capture_fbo()

glutMainLoop()