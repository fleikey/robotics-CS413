import sys
import time
import random
import math

class Program():
  __interpretation_started_timestamp__ = time.time() * 1000

  pi = 3.141592653589793
  L = None
  R = None
  W = None
  dS = None
  d_encL = None
  d_encR = None
  dist = None
  dtheta = None
  dx = None
  dx_target = None
  dy = None
  dy_target = None
  err = None
  k = None
  left = None
  oldL = None
  oldR = None
  r = None
  right = None
  theta = None
  theta_target = None
  threshold = None
  u = None
  x = None
  x_target = None
  y = None
  y_target = None

  def execMain(self):

    
    self.left = brick.sensor("A1").read()
    self.right = brick.sensor("A2").read()
    self.x = 0.0
    self.y = 0.0
    self.theta = 0.0
    self.k = 1.1
    self.oldL = brick.encoder("E3").read()
    self.oldR = brick.encoder("E4").read()
    self.r = 0.0375
    self.W = 0.194
    self.x_target = 1.0
    self.y_target = 0.5
    self.threshold = 0.05
    self.dist = 100.0
    while True:
      self.err = brick.sensor("A2").read() - self.left - (brick.sensor("A1").read() - self.right)
      self.u = self.k * self.err
      self.d_encL = brick.encoder("E3").read() - self.oldL
      self.d_encR = brick.encoder("E4").read() - self.oldR
      self.oldL = brick.encoder("E3").read()
      self.oldR = brick.encoder("E4").read()
      self.L = 2 * self.pi * self.r * self.d_encL / 360
      self.R = 2 * self.pi * self.r * self.d_encR / 360
      self.dtheta = (self.L - self.R) / self.W
      self.dS = (self.L + self.R) / 2
      self.dx = self.dS * math.cos(self.theta)
      self.dy = self.dS * math.sin(self.theta)
      self.x = self.x + self.dx
      self.y = self.y + self.dy
      self.theta = self.theta + self.dtheta
      self.dx_target = self.x_target - self.x
      self.dy_target = self.y_target - self.y
      self.dist = math.sqrt(self.dx_target * self.dx_target + self.dy_target * self.dy_target)
      self.theta_target = math.atan2(self.dy_target, self.dx_target) * (180 / self.pi)
      self.err = self.theta_target - self.theta
      brick.motor("M3").setPower(int(50 + self.u))
      
      brick.motor("M4").setPower(int(50 - self.u))
      
      script.wait(30)
      

def main():
  program = Program()
  program.execMain()

if __name__ == '__main__':
  main()
