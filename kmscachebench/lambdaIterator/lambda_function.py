# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

#lambda handler
def lambda_handler(event, context):

    #read the index value from the iterator
    myIndex = event['iterator']['index']
    myCount = event['iterator']['count']


    #increment the index
    myIndex = myIndex + 1

    #check if the index is less than the count    
    event['iterator']['continue'] = myIndex < myCount

    #update the index
    event['iterator']['index'] = myIndex

    #return the event
    return event
