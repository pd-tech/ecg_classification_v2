import os
import sys
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.optimizers import Adadelta, Adam, SGD
import numpy as np
from create_dataset import pointReader as load

def main():
    if len(sys.argv) <= 1:
        print("Usage: {0} [pointers/training.txt]".format(sys.argv[0]))
        return
        
    pointers_file     = sys.argv[1]

    
    dataset, params = load(pointers_file)[::6]  ## first & last of ((7-1) returned variables)
    print(str(len(dataset)) + " " + str(len(params)))
    print(params)

    print("Intitializing neural network...")

    model = Sequential()
    model.add(Dropout(0.1, input_shape=(7500,)))
    model.add(Dense(7500))
    model.add(Activation('tanh'))
    model.add(Dropout(0.05))
    model.add(Dense(1875))
    model.add(Activation('tanh'))
    model.add(Dense(512))
    model.add(Activation('tanh'))
    model.add(Dropout(0.01))
    model.add(Dense(128))
    model.add(Activation('tanh'))
    model.add(Dense(4)) # output // 4 categories
    model.add(Activation('softmax'))

    ''' model.add(Dense(8, input_dim=7500))
    model.add(Activation('tanh'))
    model.add(Dense(4)) # output // 4 categories
    model.add(Activation('softmax')) '''

    adadelta = Adadelta(lr=0.01)
    adam = Adam(lr=0.01)
    sgd = SGD(lr=0.01)
    model.compile(loss='binary_crossentropy', optimizer=sgd)#, metrics=['accuracy'])
    #model.compile(loss='categorical_crossentropy', optimizer=sgd)#, metrics=['categorical_accuracy'])

    print("Training neural network...")

    model.fit(np.array(dataset), np.array(params), verbose=1, batch_size=1, epochs=5)#, validation_split=0.3, shuffle=True)
    
    testx = np.array(dataset[0:1])
    testy = np.array(params[0:1])
    testx2 = np.array([dataset[-1]])
    testx3 = np.array([dataset[8]])

    print(model.predict_on_batch(np.array(dataset)))
    print(model.predict(np.array(dataset)))
    print(model.predict_classes(np.array(dataset)))
    score = model.evaluate(testx, testy)
    print(score)
    print(model.test_on_batch(testx, testy))




if __name__ == '__main__':
    main()
