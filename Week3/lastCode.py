import sys
import time
import random
import math

class Program():
  __interpretation_started_timestamp__ = time.time() * 1000

  pi = 3.141592653589793
  derivative = None
  err = None
  integral = None
  k_d = None
  k_i = None
  k_n = None
  k_p = None
  l_err = None
  left = None
  right = None
  u = None

  def execMain(self):

    
    self.left = brick.sensor("A1").read()
    self.right = brick.sensor("A5").read()
    self.integral = 0
    self.k_p = 3
    self.k_d = 0.5
    self.k_i = 0
    self.k_n = 0
    self.l_err = 0
    while True:
      self.err = brick.sensor("A5").read() - self.left - (brick.sensor("A1").read() - self.right)
      self.derivative = self.err - self.l_err
      self.integral = self.integral + self.err
      self.u = self.k_p * self.err + self.k_d * self.derivative + self.k_i * self.integral + math.pow((self.k_n * self.err), 3)
      self.l_err = self.err
      brick.motor("M3").setPower(int(20 + self.u))
      
      brick.motor("M4").setPower(int(20 - self.u))
      
      script.wait(30)
      

def main():
  program = Program()
  program.execMain()

if __name__ == '__main__':
  main()
