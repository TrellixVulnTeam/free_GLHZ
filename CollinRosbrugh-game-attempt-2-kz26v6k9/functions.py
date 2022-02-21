import time, sys

def getRoomName(playerCoords, roomData):
  try:
    roomName = roomData[str(playerCoords)]
    return roomName[0]
  except KeyError:
    return "\033[93mDEBUG: no room name exists for current room\033[0m"




def getRoomDesc(playerCoords, roomData):
  try:
    roomDesc = roomData[str(playerCoords)]
    return roomDesc[1]
  except KeyError:
    return "\033[93mDEBUG: no room description exists for current room\033[0m"




def getRoomExits(playerCoords, roomData):
  try:
    roomExits = roomData[str(playerCoords)][2]
  except KeyError:
    roomExits = "1111"

  exitList = []
  exitList[:0] = roomExits
  #breaks down "1011" into "north = true, south = false" etc

  getRoomExits.north = False
  getRoomExits.south = False
  getRoomExits.east = False
  getRoomExits.west = False

  if exitList[0] == "1":
    getRoomExits.north = True
  if exitList[1] == "1":
    getRoomExits.south = True
  if exitList[2] == "1":
    getRoomExits.east = True
  if exitList[3] == "1":
    getRoomExits.west = True
  return




def printRoomExits(playerCoords, roomData):
  try:
    exits = roomData[str(playerCoords)]
    exits = exits[2]
  except:
    print("\033[93mDEBUG: no room exit data for current room\033[0m")
    exits = "1111"

  exitList = []
  exitList[:0] = exits
  #breaks down "1011" into "north = true, south = false" etc

  north = south = east = west = ""

  if exitList[0] == "1":
    north = "NORTH "
  if exitList[1] == "1":
    south = "SOUTH "
  if exitList[2] == "1":
    east = "EAST "
  if exitList[3] == "1":
    west = "WEST"
  
  return "\033[92mExits: "+north+south+east+west+"\033[0m"





def getRoomItems(playerCoords, itemData):
  import json
  with open("roomobjectdata.json") as json_file:
    try: loadedjsondata = json.load(json_file)
    except: print('\033[31mFailed to load roomobjectdata.json.\033[0m'); return
  getRoomItems.currentRoomItems = [[],0] #the default

  roomMoney = 0
  printRoomMoney = False
  #default, will be changed

  try: currentRoomItemList = loadedjsondata[str(playerCoords)]
  except KeyError: return #this line quits the function if no room items are found to print (empty rooms will crash without this)
  
  try:
    roomMoney = currentRoomItemList[1]
    roomMoneyText = f"${roomMoney},"
    if int(roomMoney) > 0:
      printRoomMoney = True
    #if the room has more than 0 dollars, show it in the items section
  except IndexError: pass
  currentRoomItemList = currentRoomItemList[0]
  #these lines take the input [["baseballBat","baseballBat"],10] and it clips off the money variable at the end (-> roomMoney = 10), while setting the original variable to the singular list, ["baseballBat","baseballBat"]

  currentItem = 0
  export = []
  roomItemsText = []
  while True:
    try:
      export.append(itemData[currentRoomItemList[currentItem]])
      roomItemsText.append(itemData[currentRoomItemList[currentItem]].name)
    except IndexError:
      getRoomItems.currentRoomItems = [export,roomMoney]
      break
    except AttributeError:
      print("\033[31mA room object failed to load (no definition within items.py)\033[0m")
    currentItem += 1
  #this function creates 2 empty lists, one is filled with objects (export) to be exported to main.py to currentRoomItems, the other list is ued to form a list of names to be printed to display what items are present in the room
  
  sepString = ", "
  if len(roomItemsText) <= 0:
    if printRoomMoney == False:
      return
    else: roomMoneyText = roomMoneyText[:-1]
    #if there are no items in a room other than the money, it removes the comma
    #VERY USEFUL

  if len(roomItemsText) > 5:
    roomItemsText = roomItemsText[0:5]
    #cuts off all but first 5 items
    roomItemsText = sepString.join(roomItemsText)
    if printRoomMoney == True:
      print(f"\033[95mItems: {roomMoneyText} {roomItemsText}...\033[0m")
    else:
      print(f"\033[95mItems: {roomItemsText}...\033[0m")
  else:
    roomItemsText = sepString.join(roomItemsText)
    if printRoomMoney == True:
      print(f"\033[95mItems: {roomMoneyText} {roomItemsText}\033[0m")
    else:
      print(f"\033[95mItems: {roomItemsText}\033[0m")




def isValidSlot(slot):
  try: slot = int(slot)
  except:
    print("\033[31mInvalid slot!\033[0m")
    return False
  
  if slot > 3:
    print("\033[31mInvalid slot!\033[0m")
    return False
  return True




def saveProgress(slot, playerX, playerY, playerMoney, playerInventory):
  import json
  saveProgress.functionSuccess = False
  saveFailedText = "\033[31mSave failed.\033[0m"
  
  if isValidSlot(slot) == False:
    print("\033[31mCannot save to file outside of slot range.\033[0m")
    return
  
  try: saveTime = getTime('US/Pacific')
  except: saveTime = "\033[31mUnknown save time.\033[0m"
  
  with open("roomobjectdata.json") as json_file:
    try:
      roomobjectdata = json.load(json_file)
    except:
      print('\033[93mDEBUG: Failed to load file "roomobjectdata.json"\033[0m')
      print(saveFailedText)
      return

  playerInventorySaveable = []
  currentItem = 0
  while True:
    try:
      playerInventorySaveable.append(playerInventory[currentItem].reference_name)
      currentItem += 1
    except IndexError:
      break

  playerInventorySaveable = [playerInventorySaveable,playerMoney]

  saveData = [saveTime, playerX, playerY]
  saveDict = {"playerData":saveData,"playerInventory":playerInventorySaveable,"roomobjectdata":roomobjectdata}

  print("\033[92;2mSaving...\033[0m")
  try:
    with open(f"slot{slot}.json", 'w') as json_file:
      json.dump(saveDict, json_file)
  except:
    print("\033[31mopen() error, could not save data to given slot.\033[0m")
    print(saveFailedText)
    return
  
  print("\033[92mSave success!\033[0m")
  saveProgress.functionSuccess = True
  return





def loadProgress(slot, debugMode):
  import json
  loadProgress.loadSuccess = False
  loadFailedText = "\033[31mLoad Failed.\033[0m"
  
  if isValidSlot(slot) == False:
    return

  print("\033[93;2mLoading...\033[0m")
  
  try:
    with open(f"slot{slot}.json") as json_file:
      loadedjsondata = json.load(json_file)
  except:
    print("\033[31mFatal open() error.\033[0m")
    print(loadFailedText)
    return

  try:
    loadedPlayerData = loadedjsondata["playerData"]
  except:
    print("\033[31mFailed to load playerData.\033[0m")
    print(loadFailedText)
    return
  
  try:
    loadedInventoryData = loadedjsondata["playerInventory"]
  except:
    print("\033[31mFailed to load playerInventory.\033[0m")
    return
  
  try:
    loadedroomobjectdata = loadedjsondata["roomobjectdata"]
  except:
    print("\033[31mFailed to load roomobjectdata.")
    print(loadFailedText)
    return

  try:
    with open("roomobjectdata.json", 'r') as json_file:
      jsonData = json.load(json_file)
  except:
    print("\033[31mFailed to load roomobjectdata. (is file missing?)\033[0m")
    print("\033[2mCreating new rooitemdata.json with loaded data...\033[0m")
  try:
    with open("roomobjectdata.json", 'w') as json_file:
      json.dump(loadedroomobjectdata, json_file)
  except:
    print("\033[31mCould not save to roomobjectdata.json.")
    try:
      with open("roomobjectdata.json", 'w') as json_file:
        json.dump(jsonData, json_file)
        print("\033[92mroomobjectdata.json recovered, file is not corrupted.")
        return
    except:
      from lists import errormsg1
      quit(errormsg1) #something has gone horribly, horribly wrong

  try:
    loadProgress.saveTime = loadedPlayerData[0]
    loadProgress.playerX = loadedPlayerData[1]
    loadProgress.playerY = loadedPlayerData[2]
    loadProgress.playerInventory = loadedInventoryData[0]
    loadProgress.playerMoney = loadedInventoryData[1]
  except:
    print("\033[31mDEBUG: Save file misaligned, tried to load segment that doesn't exist.\033[0m")
    print("\033[31mLoad failed.\033[0m")
    return

  loadProgress.loadSuccess = True





def getSaveSlotData():
  import json
  getSaveSlotData.slot1 = ["\033[2mSlot 1 - Empty\033[0m",False]
  getSaveSlotData.slot2 = ["\033[2mSlot 2 - Empty\033[0m",False]
  getSaveSlotData.slot3 = ["\033[2mSlot 3 - Empty\033[0m",False]
  getSaveSlotData.allEmpty = False
  #the second value (the boolean) is used to determine whether the slot is filled or not without adding any extra variables. this means that in order to retrieve the text from the variable you need to specify list element 0 (ex. print(variableName[0]))

  currentSlot = 1
  
  while currentSlot <= 3:
    slotName = f"slot{currentSlot}.json"
    try:
      with open(slotName) as json_file:
        loadedjsondata = json.load(json_file)
        loadedPlayerData = loadedjsondata["playerData"]
        #loads the list in format ["10:18AM, 2022-01-20", 666, 665, 400] and it takes the first list element (the date and time the file was saved) and it uses the function to return that as the file name to display
      if currentSlot == 1:
        getSaveSlotData.slot1 = [f"Slot 1 - {loadedPlayerData[0]}",True]
      elif currentSlot == 2:
        getSaveSlotData.slot2 = [f"Slot 2 - {loadedPlayerData[0]}",True]
      elif currentSlot == 3:
        getSaveSlotData.slot3 = [f"Slot 3 - {loadedPlayerData[0]}",True]
    
    except: pass
    currentSlot += 1
  
  if getSaveSlotData.slot1[1] == False and getSaveSlotData.slot2[1] == False and getSaveSlotData.slot3[1] == False:
    getSaveSlotData.allEmpty = True
  return




def clearSlot(slot):
  if isValidSlot(slot) == True:
    print("\033[93;2mClearing slot...\033[0m")
    try:
      with open(f"slot{slot}.json", "w") as f:
        print("\033[92mSlot cleared!\033[0m")
    except:
      print("\033[31mFailed to clear slot. (is file now corrupted??)")
  else:
    print("\033[31mInvalid slot!\033[0m")
  return





def printSaveSlotList():
  getSaveSlotData()
  printSaveSlotList.allEmpty = getSaveSlotData.allEmpty

  print(f"\n{getSaveSlotData.slot1[0]}")
  print(getSaveSlotData.slot2[0])
  print(f"{getSaveSlotData.slot3[0]}\n")
  
  if printSaveSlotList.allEmpty == True:
    print("\033[31mAll slots are empty!\033[0m")
  return






def getTime(timeZone):
  from datetime import date, datetime
  import pytz

  today = date.today()

  tz = pytz.timezone(timeZone)
  datetime_tz = datetime.now(tz)

  hour = int(datetime_tz.strftime("%H"))
  minute = int(datetime_tz.strftime("%M"))

  if hour > 12:
    hour -= 12
    meridiem = "PM"
  else:
    meridiem = "AM"
  
  if minute < 10:
    minute = f"0{minute}"

  try:
    return f"{hour}:{minute}{meridiem} {today}"
  except:
    return "\033[31mFailed to retrieve date.\033[0m"





def printColor(string, color):
  if color.lower() == "red":
    print("\033[31m"+str(string)+"\033[0m") #red
  elif color.lower() == "ltred":
    print("\033[91m"+str(string)+"\033[0m") #light red
  elif color.lower() == "yellow":
    print("\033[93m"+str(string)+"\033[0m") #yellow
  elif color.lower() == "drkyellow":
    print("\033[33m"+str(string)+"\033[0m") #dark yellow
  elif color.lower() == "green":
    print("\033[92m"+str(string)+"\033[0m") #green
  elif color.lower() == "drkgreen":
    print("\033[32m"+str(string)+"\033[0m") #dark green
  elif color.lower() == "blue":
    print("\033[34m"+str(string)+"\033[0m") #blue
  elif color.lower() == "ltblue":
    print("\033[94m"+str(string)+"\033[0m") #light blue
  elif color.lower() == "cyan":
    print("\033[96m"+str(string)+"\033[0m") #cyan
  elif color.lower() == "drkcyan":
    print("\033[36m"+str(string)+"\033[0m") #dark cyan
  elif color.lower() == "magenta":
    print("\033[95m"+str(string)+"\033[0m") #magenta
  elif color.lower() == "drkmagenta":
    print("\033[35m"+str(string)+"\033[0m") #dark magenta
  elif color.lower() == "black":
    print("\033[90m"+str(string)+"\033[0m") #black





def getItem(playerInput, playerCoords, playerInventory, currentRoomItems, playerBag, playerMoney, itemData, debugMode):
  import json
  
  addItemToInventory = True
  getItem.playerInventory = playerInventory #a list of objects
  getItem.currentRoomItems = currentRoomItems #a list of objects[0] and an int value[1]
  getItem.playerBag = playerBag #an object
  getItem.playerMoney = playerMoney #int
  getItem.functionSuccess = False
  #if the function fails and nothing is updated, these lines mark the default state for the variables

  try: roomMoney = currentRoomItems[1] #stores money value in a variable
  except IndexError: roomMoney = 0 #if no money value is specified, money is set to 0
  currentRoomItems = currentRoomItems[0] #removes money value from the list

  playerInput = playerInput[4:]
  #this line trims "get baseball bat" into "baseball bat"
  
  currentItem = 0
  while True:
    try:
      if playerInput == str(currentRoomItems[currentItem].name.lower()):
        #checks if the player's input matches the name of an object (in lowercase)
        pickedUpItem = currentRoomItems.pop(currentItem)
        if debugMode == True: print("\033[93mDEBUG: popped specified item from currentRoomItem list\033[0m")
        break
        #picks up the player's requested object and removes it from the "currentRoomItems" list (in preperation for saving)
      currentItem += 1
    except IndexError:
      if debugMode == True: print("\033[93mDEBUG: could not find item name in currentRoomItems list\033[0m")
      print("\033[31mYou don't see that here!\033[0m")
      return

  try:
    if pickedUpItem.isKeyItem == True:
      if debugMode == True: print("\033[93mDEBUG: pickedUpItem is key item\033[0m")
      
      if pickedUpItem.itemType == "backpack":
        if debugMode == True: print("\033[93mDEBUG: pickedUpItem is backpack\033[0m")
        
        if pickedUpItem.itemValue >= playerBag.itemValue:
          carryingCapacityIncrease=int(pickedUpItem.itemValue)-int(playerBag.itemValue)
          playerBag = pickedUpItem
          if debugMode == True: print("\033[93mDEBUG: updated playerBag variable\033[0m")

          if pickedUpItem.reference_name == "holdingBag":
            print("\033[92mYour carrying capacity has increased by »’íÙ}Šñd²žp%æ‰\033[0m")
          else:
            print(f"\033[92mYour carrying capacity has increased by {carryingCapacityIncrease}!\033[0m")
  
        else:
          if debugMode == True: print("\033[93mDEBUG: the bag specified has less slots than player's bag, this is not allowed\033[0m")
          print("\033[31mThis bag is worse than your current bag!\033[0m")
          return
        addItemToInventory = False
        
    #this code applies to key items and can be expanded to give the player items that will not be added to their inventory, but instead update a different variable
    else: pass
  except AttributeError: pass
  #if it ain't a key item, it moves on

  currentItem = 0
  updatedRoomItems = []
  while True:
    try:
      updatedRoomItems.append(currentRoomItems[currentItem].reference_name)
    except IndexError:
      break
    currentItem += 1
  #this function breaks down the list of currentRoomItems into a list of reference names ["baseballBat","baseballBat","baseballBat"]

  currentItem = 0
  currentRoomItems = []
  while True:
    try:
      currentRoomItems.append(itemData[updatedRoomItems[currentItem]])
    except IndexError:
      break
    currentItem += 1
  currentRoomItems = [currentRoomItems,roomMoney]
  #this function reassembles the updated reference name list as objects to be sent to currentRoomItems in main.py, like [<objects.Weapon object at 0x7fa626cd8e50>, <objects.Item object at 0x7fa626cd8a00>]

  updatedDict = {str(playerCoords):[updatedRoomItems,roomMoney]}
  
  with open("roomobjectdata.json") as json_file:
    jsonData = json.load(json_file)
    updatedJsonData = jsonData
  try:
    with open("roomobjectdata.json", "w") as json_file:
      updatedJsonData.update(updatedDict)
      json.dump(updatedJsonData, json_file)
      #tries to update the roomobjectdata.json file as a dictionary
        
    if addItemToInventory == True:
      print(f"\033[96mPicked up {pickedUpItem.name}!\033[0m")
      playerInventory.append(pickedUpItem)
      #this boolean exists as to not add key items to your regular inventory
    else:
      if debugMode == True: print("\033[93mDEBUG: is key item, item will not being added to playerInventory\033[0m")
        
    getItem.playerInventory = playerInventory
    getItem.currentRoomItems = currentRoomItems
    getItem.playerBag = playerBag
    getItem.functionSuccess = True
    return
    #updates variables in main.py through using this function
  except:
    with open("roomobjectdata.json", "w") as json_file:
      json.dump(jsonData, json_file)
    print("\033[31mDEBUG: Fatal error updating roomobjectdata.json! Changes have not been applied to prevent file corruption.\033[0m")





def getMoney(playerInput, playerCoords, playerInventory, currentRoomItems, playerMoney, debugMode):
  import json

  getMoney.playerMoney = playerMoney
  getMoney.currentRoomItems = currentRoomItems
  getMoney.functionSuccess = False

  if debugMode == True: print("\033[93mDEBUG: getMoney() called\033[0m")

  try: roomMoney = currentRoomItems[1] #stores money value in a variable
  except IndexError: roomMoney = 0 #if no money value is specified, money is set to 0
  currentRoomItems = currentRoomItems[0] #removes money value from the list

  if roomMoney > 0:
    try:
      if playerInput[5:] == "" or abs(int(playerInput[5:])) > roomMoney:
        playerInput = roomMoney
      else:
        playerInput = abs(int(playerInput[5:]))
        #if the player enters nothing or a number that is too large, this function will get all the availible money there is in the current room
      
      if debugMode == True: print(f"\033[93mDEBUG: room money before: {roomMoney}\033[0m")
      roomMoney -= playerInput
      if debugMode == True: print(f"\033[93mDEBUG: room money after: {roomMoney}\033[0m")
      if debugMode == True: print(f"\033[93mDEBUG: player money before: {playerMoney}\033[0m")
      playerMoney += playerInput
      if debugMode == True: print(f"\033[93mDEBUG: player money after: {playerMoney}\033[0m")
      #the calculations for how much money is added/removed
        
      if playerMoney >= 0:
        pass
      else:
        from lists import errormsg1
        print(f"\033[93mDEBUG: {errormsg1}\033[0m")
        quit("\nhttps://xkcd.com/2200/")
        #this happens if the player's wallet balance becomes negative

      with open("roomobjectdata.json") as json_file:
        jsonData = json.load(json_file)
        updatedJsonData = jsonData
        
      try: updatedDict = {str(playerCoords):[jsonData[str(playerCoords)][0],roomMoney]}
      except KeyError: updatedDict = {str(playerCoords):[[],roomMoney]}
        
      try:
        if debugMode == True: print("\033[93mDEBUG: updating roomobjectdata.json\033[0m")
        with open("roomobjectdata.json", "w") as json_file:
          updatedJsonData.update(updatedDict)
          json.dump(updatedJsonData, json_file)
          
          getMoney.playerMoney = playerMoney
          getMoney.currentRoomItems = [currentRoomItems,roomMoney]
          getMoney.functionSuccess = True
          print(f"\033[96mYou pick up ${playerInput} before anyone notices.\033[0m")
        
        if debugMode == True: print("\033[93mDEBUG: updated roomobjectdata.json\033[0m")
        if getMoney.currentRoomItems[1] > 0:
          print(f"\033[95m${getMoney.currentRoomItems[1]} remains in the room.\033[0m")
        return
      except:
        with open("roomobjectdata.json", "w") as json_file:
          json.dump(jsonData, json_file)
          print("\033[31mFatal error updating roomobjectdata.json! Changes have not been applied to prevent file corruption. (file most likley would have been overwritten with garbage)\033[0m")
        return

    except ValueError:
      print("\033[31mInvalid number!\033[0m")
      return
  
  else:
    print("\033[31mYou don't see that here!\033[0m")
    return






def dropItem(playerInput, playerCoords, playerInventory, itemData, currentRoomItems, playerMoney, debugMode):
  dropItem.playerInventory = playerInventory
  dropItem.currentRoomItems = currentRoomItems
  dropItem.playerMoney = playerMoney
  dropItem.functionSuccess = False #will be updated later
  
  try: roomMoney = currentRoomItems[1]
  except IndexError: roomMoney = 0
  currentRoomItems = currentRoomItems[0]

  currentItem = 0
  while True:
    try:
      if playerInput[5:] == playerInventory[currentItem].name.lower():
        droppedItem = playerInventory.pop(currentItem)
        if debugMode == True: print("\033[93mDEBUG: removed item from player's inventory\033[0m")
        #looks to see if player's inventory contains item to drop
        break
      else:
        currentItem += 1
    except IndexError:
      from lists import apst
      print(f'\033[31mYou don{apst}t have "{playerInput[5:]}"!\033[0m')
      return
  
  currentItem = 0
  convertedRoomItems = []
  while True:
    try:
      convertedRoomItems.append(currentRoomItems[currentItem].reference_name)
        #converts the entire "currentRoomItems" list into a list of reference_names (baseballBat, baseballGlove, etc.)
    except IndexError:
      break
    currentItem += 1
  
  if debugMode == True: print(f"\033[93mDEBUG: convertedRoomItems: {convertedRoomItems}\033[0m")

  try: convertedRoomItems.append(droppedItem.reference_name)
  except:
    dropItem.functionSuccess = False
    print("\033[31mError, cannot add dropped item to convertedRoomItemsList. Item cannot be saved to roomobjectdata.json\033[0m")
    playerInventory.append(droppedItem)
    dropItem.playerInventory = playerInventory
    return
  #adds the dropped item to the convertedRoomItem list (in preperation to save to roomobjectdata.json) if this line doesn't work, nothing in this function works
  
  convertedRoomItemsDict = {str(playerCoords):[convertedRoomItems,roomMoney]}
  #converts the "convertedRoomItems" list into a dictionary to be merged into roomobjectdata.json
  
  with open("roomobjectdata.json") as json_file:
    import json
    jsondata = json.load(json_file)
    updatedJsondata = jsondata
  try:
    with open("roomobjectdata.json", "w") as json_file:
      updatedJsondata.update(convertedRoomItemsDict)
      if debugMode == True: print(f"\033[93mDEBUG: updatedJsondata: {updatedJsondata}\033[0m")
      json.dump(updatedJsondata, json_file)
      #loads roomobjectdata.json, updates it with the new dictionary with the new item
  except:
    with open("roomobjectdata.json", "w") as json_file:
      json.dump(jsondata, json_file)
      print("\033[31mDEBUG: Fatal error updating roomobjectdata.json! Changes have not been applied to prevent file corruption.\033[0m")
      playerInventory.append(droppedItem)
  
  dropItem.playerInventory = playerInventory
  dropItem.currentRoomItems = [convertedRoomItems,roomMoney] #the old currentRoomItems list had its money value chopped off, so use convertedRoomItems instead
  dropItem.functionSuccess = True
  #updates these variables in main.py

  print(f"\033[96mDropped {droppedItem.name}!\033[0m")




def dropMoney(playerInput, playerCoords, playerInventory, currentRoomItems, playerMoney, debugMode):
  import json

  dropMoney.playerMoney = playerMoney
  dropMoney.currentRoomItems = currentRoomItems
  dropMoney.functionSuccess = False

  if debugMode == True: print("\033[93mDEBUG: dropMoney() called\033[0m")

  try: roomMoney = currentRoomItems[1] #stores money value in a variable
  except IndexError: roomMoney = 0 #if no money value is specified, money is set to 0
  currentRoomItems = currentRoomItems[0] #removes money value from the list

  if playerMoney > 0:
    try:
      if playerInput[6:] == "" or abs(int(playerInput[6:])) > playerMoney:
        playerInput = playerMoney
      else:
        playerInput = abs(int(playerInput[6:]))
        #if the player types in nothing or a number that is too large it will default to dropping all the money the player has- no more, no less

      if debugMode == True: print(f"\033[93mDEBUG: room money before: {roomMoney}\033[0m")
      playerMoney -= playerInput
      if debugMode == True: print(f"\033[93mDEBUG: room money after: {roomMoney}\033[0m")
      if debugMode == True: print(f"\033[93mDEBUG: player money before: {playerMoney}\033[0m")
      roomMoney += playerInput
      if debugMode == True: print(f"\033[93mDEBUG: player money after: {playerMoney}\033[0m")
      #the calculations for how much money is added/removed
        
      if playerMoney >= 0:
        pass
      else:
        from lists import errormsg1
        print(f"\033[93mDEBUG: {errormsg1}\033[0m")
        quit("\nhttps://xkcd.com/2200/")
        #this happens if the player's wallet balance becomes negative

      with open("roomobjectdata.json") as json_file:
        jsonData = json.load(json_file)
        updatedJsonData = jsonData
      
      try: updatedDict = {str(playerCoords):[jsonData[str(playerCoords)][0],roomMoney]}
      except KeyError: updatedDict = {str(playerCoords):[[],roomMoney]}
        
      try:
        if debugMode == True: print("\033[93mDEBUG: updating roomobjectdata.json\033[0m")
        with open("roomobjectdata.json", "w") as json_file:
          updatedJsonData.update(updatedDict)
          json.dump(updatedJsonData, json_file)
          
          dropMoney.functionSuccess = True
          dropMoney.playerMoney = playerMoney
          dropMoney.roomMoney = roomMoney
          dropMoney.currentRoomItems = [currentRoomItems,roomMoney]
          print(f"\033[96mYou leave ${playerInput} on the ground. Good luck paying rent this month!\033[0m")
        
        if debugMode == True: print("\033[93mDEBUG: updated roomobjectdata.json\033[0m")
        if dropMoney.currentRoomItems[1] > 0:
          print(f"\033[95m${dropMoney.currentRoomItems[1]} lies in the center of the room.\033[0m")
        return
      except ValueError:
        with open("roomobjectdata.json", "w") as json_file:
          json.dump(jsonData, json_file)
          print("\033[31mFatal error updating roomobjectdata.json! Changes have not been applied to prevent file corruption. (file most likley would have been overwritten with garbage)\033[0m")
        return

    except ValueError:
      print("\033[31mInvalid number!\033[0m")
      return
  
  else:
    print("\033[31mBro you literally have no money to drop fr you actually broke rn\033[0m")
    return




def properNoun(string):
  if string == "": return "" #no need to continue
  string = string.split(" ")
  
  newString = []
  for x in string:
    newString.append(x[0:1].upper()+x[1:])
  string = ""
  for x in newString:
    string = string + x + " "
  
  return string[:-1]




def xpToLevelUp(level):
  xpToLevelUp = level ** 2.5 + 100 + 5 * level - 6
  return int(round(xpToLevelUp,0))
  #print(f"Level {placeValue(level)}: {placeValue(int(round(xpToLevelUp,0)))}xp")




def didPlayerLevelUp(currentLevel, xp):
  if xpToLevelUp(currentLevel) < xp:
    return True




def placeValue(number):
  import math
  try: number = str(number)
  except: return "\033[31mbro fr what the fuck is this\033[0m"
  if len(number) <= 3: return number
  commas = math.floor(len(number)/3)

  output = []
  for x in range(commas):
    x = number[-3:] #gets last 3 chars of the string
    number = number[:-3] #trims them off
    output.insert(0, x) #stores them in list at first position
  
  output.insert(0, number) #adds the last non-divisible-by-3 part onto the front
  
  export = ""
  for x in output:
    export += x + ","
  
  if export[0:1] == ",": export = export[1:]
  #fixes a bug where it outputs like ",208,975" instead of "208,975"

  return export[:-1]




def clearConsole():
    from os import system, name
    if name == 'nt':
      _ = system('cls')
    else:
      _ = system('clear')
    #this code is from https://www.geeksforgeeks.org/clear-screen-python/, I did not write it myself and so I do not claim to




def fancyPrint(text, delay=0.04):
  for x in text:
    sys.stdout.write(x)
    sys.stdout.flush()
    time.sleep(delay)




def statusBar(persentage, size, color, bg):
  char = "█"; bar = ""
  for x in range(size):
    bar += char
  ratio = 100/size
  persentage = int(persentage/ratio) #determines the number of green boxes to display
  if persentage < 0: persentage = 0 #if the boxes to print are less than 0, print no boxes instead of a negative
  return f"{color}{bar[0:persentage]}{bg}{bar[persentage:size]}\033[0m"



def showCursor():
  print("\033[?25h",end="")
def hideCursor():
  print("\033[?25l",end="")



def space(int):
  export = char = " "
  for x in range(0,int-1):
    export += char
  return export