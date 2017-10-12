import traceback
from collections import OrderedDict

TTL = 86400
packet_id = 0x1010

class DNSPacket:

    def __init__(self, rawb):
        '''при инициализации с байтовым аргументом тот парсится в словарь вида self.__records'''
        self.__data = rawb        
        self.classes = {b'\x00\x01': 'IN'}
        self.types = {b'\x00\x01': 'A',
                      b'\x00\x02': 'NS',
                      b'\x00\x05': 'CNAME',
                      b'\x00\x06': 'SOA',
                      b'\x00\x0c': 'PTR',
                      b'\x00\x0f': 'MX',
                      b'\x00\x1c': 'AAAA',
                      b'\x00\xfc': 'AXFR'}
        
        self.__records = OrderedDict(
            {'Queries': {
                'fields': ('Name', 'Type', 'Class'), 'data': []},
            'Answers': {
                'fields': ('Name', 'Type', 'Class', 'TTL', 'Data length', 'Address'), 'data': []},
            'Authoritative NS': {
                'fields': ('Name', 'Type', 'Class', 'TTL', 'Data length', 'Name Server'), 'data': []},
            'Additional records': {
                'fields': ('Name', 'Type', 'Class', 'TTL', 'Data length', 'Address', 'CNAME'), 'data': []}
            })
        
        self.readOffs = 0
        self.offsets = {}
        self.hdrs = [None]*6
        
        if type(self.__data) != bytes:
            self.__createPacket()
        self.__parseAll()
            
    @staticmethod
    def strEncode(bStr) -> bytes:
        '''кодирует строку в формат (длина_до_точки)имя1.(длина_до_точки)имя2...\x00'''
        return b''.join(itob(len(i))+i.encode('ascii') for i in bStr) + b'\x00'
    
    def __createPacket(self):
        '''при инициализации объекта с аргументами в виде 'имя', 'тип', 'класс' те сериализуются в бинарную строку'''
        
        self.strarr = [itob(packet_id, 2), #transaction ID
                       b'\x00\x10', #no flags
                       b'\x00\x01', #only questions
                       b'\x00'*6, #no answers
                       self.strEncode(self.__data[0].split('.')),
                       getkeyByValue(self.types, self.__data[1]),
                       b'\x00\x01'
        ]
        self.__data = b''.join(self.strarr)
        packet_id += 1

    def removeField(self, dkey):
        '''удаляет из словаря ключ f'''
        
        self.__records[dkey]['data'].clear()

    def addField(self, dkey, vname=None, vtype=None, data=None, ttl=86400, dlen=4):
        '''добавляет параметры в self.__records[dkey]'''        
        if dkey == 'Answers':
            if vname == None:
                self.__records[dkey]['data'].append(data)
            self.to_app = {'Name': vname,
                           'Type': vtype, 
                           'Class': 'IN',
                           'TTL': ttl,
                           'Data length': dlen}
            if vtype == 'A':
                self.to_app['Address'] = data
            elif vtype == 'CNAME':
                self.to_app['CNAME'] = data
            self.__records[dkey]['data'].append(self.to_app)
        else:
            self.__records[dkey]['data'] = data
        
    def setPointers(self, bstr) -> str:
        '''расстановка указателей на строки в бинарном представлении пакета, ищет в дополнительном буфере (не в основном!)'''
        for i in range(len(bstr)):
            self.text = self.strEncode(bstr[i:])
            if self.text in self.offsets.keys() and self.text in bytes(self.bindata):
                return self.strEncode(bstr[:i])[:-1] + self.offsets[self.text]
            self.doffs = bytes(self.bindata).find(self.text)
            if self.doffs != -1:
                #print('bstr:', self.itob(0xc000 | self.doffs, 2), i, bstr[:i])
                self.offsets[self.text] = itob(0xc000 | self.doffs, 2)
                return self.strEncode(bstr[:i])[:-1] + self.offsets[self.text]
        return self.strEncode(bstr)
        
    def serializedata(self, indict=None):
        '''сериализует словарь в бинарную строку'''
        if indict == None:
            indict = self.__records
        self.bindata = bytearray()
        self.strs = [indict['ID'],
                     indict['Flags'],
                     itob(len(indict['Queries']), 2),
                     itob(len(indict['Answers']), 2),
                     itob(len(indict['Authoritative NS']), 2),
                     itob(len(indict['Additional records']), 2)
                     ]
        for i in self.strs:
            self.bindata.extend(i)
        for i in range(4):
            for j in range(btoi(self.strs[i+2])):
                for k in self.fieldsorder[i]:
                    try:
                        self.itm = indict[self.rnames[i]][j][k]
                    except:
                        continue
                    if k == 'Type':
                        self.itm = getkeyByValue(self.types, self.itm)
                    elif k == 'Class':
                        self.itm = b'\x00\x01'
                    elif k == 'TTL':
                        self.itm = itob(self.itm, 4)
                    elif k == 'Data length':
                        self.itm = itob(self.itm, 2)
                    elif k == 'Address':
                        if '.' in self.itm:
                            self.itm = b''.join(map(lambda a: itob(int(a), 1), self.itm.split('.')))
                        elif ':' in self.itm:
                            self.itm = b''.join(map(lambda a: itob(int(a, 16), 1), self.itm.split(':')))  
                    elif k == 'Name' or k == 'Name server' or k == 'CNAME':
                        #print(self.itm, self.bindata)
                            self.itm = self.setPointers(self.itm.split('.'))
                    self.bindata.extend(self.itm)
            self.__data = bytes(self.bindata)
        
    def __substr(self, strlen) -> str:
        '''как головка, читающая ленту: возвращается n следующих элементов строки'''
        self.sub = self.__data[self.readOffs:self.readOffs+strlen]
        self.readOffs += strlen
        return self.sub
    
    def getItemByOffset(self, bStr) -> str:
        if bStr not in self.offsets.keys():
            self.offsets[bStr] = self.strDecode(self.__data[btoi(bStr) & 0x3fff:])
        return self.offsets[bStr]

    def strDecode(self, bStr) -> bytes:
        '''парсит строку из пакета (с длинами до точек и указателями) в читабельную'''
        self.result = []
        self.ptr = None
        while self.ptr != 0:
            print(bStr)
            self.ptr = bStr[0]
            if self.ptr & 0xc0 == 0xc0:
                self.result.append(self.getItemByOffset(bStr[:2]))
                self.readOffs += 2
                break
            self.readOffs += self.ptr+1
            self.result.append(bStr[1:self.ptr+1])
            print(self.result)
            bStr = bStr[self.ptr+1:]
        #self.readOffs += 1
        return b'.'.join(self.result)

    def __parseAll(self):
        self.temp = self.__substr(12)
        try:
            for i in range(len(self.hdrs)):
                self.hdrs[i] = self.temp[i*2:(i+1)*2]
                if i>=2:
                    self.hdrs[i] = btoi(self.hdrs[i])
            self.__records['ID'] = self.hdrs[0]
            self.__records['Flags'] = self.hdrs[1]
            self.hdrs = self.hdrs[2:]
            for counter in range(len(self.hdrs)):
                for _ in range(self.hdrs[counter]):
                    self.fields = {}
                    self.fields['Name'] = self.strDecode(self.__data[self.readOffs:]).decode('ascii')
                    self.temp = self.__substr(4)
                    self.fields['Type'] = self.types[self.temp[:2]]
                    self.fields['Class'] = self.classes[self.temp[2:4]]
                    if counter > 0: 
                        self.temp = self.__substr(6)
                        self.fields['TTL'] = btoi(self.temp[:4])
                        self.fields['Data length'] = btoi(self.temp[4:6])
                        if counter == 2:
                            self.fields['Name server'] = self.strDecode(self.__substr(self.fields['Data length'])).decode('ascii')
                        else:
                            if self.fields['Type'] == 'CNAME':
                                self.fields['CNAME'] = self.strDecode(self.__substr(self.fields['Data length'])).decode('ascii')
                            else:
                                if self.fields['Data length'] == 16:
                                    self.fields['Address'] = ':'.join(hex(i)[2:] for i in self.__substr(16))
                                else:
                                    self.fields['Address'] = '.'.join(str(i) for i in self.__substr(4))
                    self.__records[self.rnames[counter]]['data'].append(self.fields)
        except ArithmeticError:
            traceback.print_exc()
            print('Error was in', self.readOffs)

    def getParsedData(self, arrs=None, nkey=None, *cond): #TODO: што
        try:
            if nkey == None:
                if arrs == None:
                    return self.__records
                else:
                    return self.__records[arrs]['data']
            if len(cond) == 0:
                return [i[nkey] for i in self.__records[arrs]]
            else:
                return [i[nkey] for i in self.__records[arrs] if i[cond[0]] == cond[1]]
        except:
            return []
    
    def getRawData(self):
        return self.__data
    

    
def getkeyByValue(dic, val):
    for k,v in dic.items():
        if v == val:
            return k
    return b''

def btoi(bStr):
    return int.from_bytes(bStr, byteorder='big')

def itob(num, s=0):
    if s == 0:
        return num.to_bytes(num//256+1, byteorder='big')
    else:
        return num.to_bytes(s, byteorder='big')
