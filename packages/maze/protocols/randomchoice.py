# Example protocol for maze training
# Author: Ariel Burman


from mazeprotocols import MazeProtocols
import time

import logging
logger=logging.getLogger(__name__)

PROTOCOL_NAME= 'RandomChoice'
PROTOCOL_VERSION = '1.0'

import numpy as np


class RandomChoice (MazeProtocols):
  def init(self):
    # initialization
    # put here the code you want to run only once, at first
    logger.info('Protocol: {a}, Version: {b}'.format(a=PROTOCOL_NAME,b=PROTOCOL_VERSION))
    self.rewardWindow = 4.0
    logger.info('Reward Window: {a}'.format(a=self.rewardWindow))
    self.state = 'start'
    self.openGateFast('IUL')
    self.openGateFast('IUR')
    self.openGateFast('OUL')
    self.openGateFast('OUR')
    self.openGateFast('OBL') # maybe closed
    self.openGateFast('OBR') # maybe closed
    self.closeGateFast('IBL')
    self.closeGateFast('IBR')
    self.rewardDone = False
    self.toneDone = False
    self.multidropNum = 2
    self.setMultiDrop(self.multidropNum)
    logger.info('set multidrop to {a}'.format(a=self.multidropNum))
    self.trialNum = 0
    self.timeInitTraining = 0
    self.trialInit = 0
    self.currentTrial = ''
    self.trialsCount = {'L':0,'R':0}
    self.trialsCorrect = {'L':0,'R':0}
    self.trials = []
    self.addTone(2,duration=1.0,freq=1000,volume=0.7)
    self.addTone(1,duration=1.0,freq=8000,volume=1.0)
    logger.info('Tone 1 asociated with Left 8 kHz')
    logger.info('Tone 2 asociated with Right 1 kHz')
    time.sleep(.1)
    self.myLastSensor = None
    pass # leave this line in case 'init' is empty

  def exit(self):
    # ending protocol. cleanup code. probably loggin stats.
    self.printStats()
    logger.info(self.trials)
    print('bye bye')
    pass # leave this line in case 'exit' is empty

#  def buttonHandler(obj,button):
#      ''' If you dont use a handler this function should be commented'''
#      pass
#
#  def sensorHandler(self,sensor):
#      ''' If you dont use a handler this function should be commented'''
#      print('sensor activated {a}'.format(a=sensor))
#      print(id(self))
#      print(dir(self))
#      self.trialNum +=1
#      self.myLastSensor = sensor
#      pass

  # Write your own methods

  
  def chooseTone(self,trial):
    return round(np.random.random()+1)

  def myFunction(self,param):
    logger.debug(param)

  def startTrial(self):
    self.trialNum +=1
    nextTone=self.chooseTone(self.trialNum)
    if nextTone == 1:
        self.currentTrial = 'L'
    else:
        self.currentTrial = 'R'
        
    self.trials.append([self.trialNum, self.currentTrial,0])
    self.playSound(nextTone)
    logger.info('Played tone {a} trialNum {b}'.format(a=nextTone,b=self.trialNum))
    self.trialInit = time.time()
    self.trialsCount[self.currentTrial] +=1

  def printStats(self):
    tt = time.time() - self.timeInitTraining
    msg1 = 'Trial Num: {c} | Total time = {a} minutes {b} seconds'.format(a=int(tt/60),b=int(tt)%60,c = self.trialNum)
    msg2 = 'Total trial: {a}/{b} = {c}% | Left: {d}/{e} = {f}% | Right: {g}/{h} = {i}%'.format(
        a = (self.trialsCorrect['L']+self.trialsCorrect['R']),
        b = (self.trialsCount['L']+self.trialsCount['R']),
        c=round(100*(self.trialsCorrect['L']+self.trialsCorrect['R'])/(self.trialsCount['L']+self.trialsCount['R']+0.0001)),
        d = self.trialsCorrect['L'] ,
        e = self.trialsCount['L'] ,
        f = round(100*self.trialsCorrect['L']/(self.trialsCount['L']+0.0001)),
        g = self.trialsCorrect['R'] ,
        h = self.trialsCount['R'] ,
        i = round(100*self.trialsCorrect['R']/(self.trialsCount['R']+0.0001)))
    print (msg1)
    print (msg2)
    logger.info(msg1)
    logger.info(msg2)

  def run(self):
    ''' 
    This is the main loop. It should have a 'while True:' statement
    also it is recomended to have a time.slep(.05) or bigger delay
    
    '''
    try:
      self.trialNum = 0
      # waiting to rat to pass the sensor
      #while self.getLastSensorActive()!='C':
      while self.isSensorActive('C')==False:
          pass
      self.timeInitTraining = time.time()
      self.startTrial()
      while True:
        self.myFunction(self.state)
        if self.state == 'start':
          self.rewardDone = False

          #if self.myLastSensor=='UL':
          if self.isSensorActive('UL')==True:
            logger.info('Rat at {a}'.format(a='UL'))
            #the rat went left
            self.closeGateFast('IBL')
            self.closeGateFast('IBR')
            self.closeGateFast('IUR')
            self.openGateFast('OBL')
            self.state='going left'
            logger.info('reward on left')
          #elif self.myLastSensor=='UR':
          elif self.isSensorActive('UR')==True:
            logger.info('Rat at {a}'.format(a='UR'))
            #the rat went right
            self.closeGateFast('IBL')
            self.closeGateFast('IBR')
            self.closeGateFast('IUL')
            self.openGateFast('OBR')
            self.state='going right'
            # check for reward
            logger.info('reward on right')

        elif self.state == 'going left':
          #if self.myLastSensor=='L':
          if self.isSensorActive('L')==True:
            logger.info('Rat at {a}'.format(a='L'))
            self.closeGateFast('IUL')
            self.openGateFast('IBL')
            self.state = 'reward left'
            if self.rewardDone == False:
              self.rewardDone = True
              now = time.time()
              if now > (self.trialInit + self.rewardWindow):
                logger.info('Not Giving reward, exceeding window')
              elif self.currentTrial=='R':
                logger.info('Not Giving reward, wrong side')
              else:
                logger.info('Giving reward')
                self.multiDrop('L')
                self.trialsCorrect['L'] += 1
                self.trials[-1][2] = 1
              self.printStats()

        elif self.state == 'reward left':
          #if self.myLastSensor=='BL':
          if self.isSensorActive('BL')==True:
            logger.info('Rat at {a}'.format(a='BL'))
            self.openGateFast('IUL')
            self.openGateFast('IUR')
            self.closeGateFast('OUL')
            self.state = 'returning left'

          #if self.myLastSensor=='L':
          if self.isSensorActive('L')==True:
            logger.info('Rat at {a}'.format(a='L'))

        elif self.state == 'returning left':
          #if self.myLastSensor=='C':
          if self.isSensorActive('C')==True:
            logger.info('Rat at {a}'.format(a='C'))
            self.closeGateFast('OBL')
            self.openGateFast('OUL')
            self.openGateFast('OUR')
            self.state = 'start'
            self.startTrial()


        elif self.state == 'going right':
          #if self.getLastSensorActive()=='R':
          if self.isSensorActive('R')==True:
            logger.info('Rat at {a}'.format(a='R'))
            self.closeGateFast('IUR')
            self.openGateFast('IBR')
            self.state = 'reward right'
            if self.rewardDone == False:
              now = time.time()
              self.rewardDone = True
              if now > (self.trialInit + self.rewardWindow):
                logger.info('NOT Giving reward, exceeding window')
              elif self.currentTrial=='L':
                logger.info('Not Giving reward, wrong side')
              else:
                logger.info('Giving reward')
                self.multiDrop('R')
                self.trialsCorrect['R'] += 1
                self.trials[-1][2] = 1
              self.printStats()

        elif self.state == 'reward right':
          #if self.getLastSensorActive()=='BR':
          if self.isSensorActive('BR')==True:
            logger.info('Rat at {a}'.format(a='BR'))
            self.openGateFast('IUL')
            self.openGateFast('IUR')
            self.closeGateFast('OUR')

            self.state = 'returning right'

          #if self.getLastSensorActive()=='R':
          if self.isSensorActive('R')==True:
            logger.info('Rat at {a}'.format(a='R'))
                
        elif self.state == 'returning right':
          #if self.getLastSensorActive()=='C':
          if self.isSensorActive('C')==True:
            logger.info('Rat at {a}'.format(a='C'))
            self.closeGateFast('OBR')
            self.openGateFast('OUL')
            self.openGateFast('OUR')
            self.state = 'start'
            self.startTrial()

        time.sleep(.01)

    except Exception as e:
      logger.error(e)
      print(e)
