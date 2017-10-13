import traceback
from collections import OrderedDict

TTL = 86400
packet_id = 0x1010


def btoi(bStr):
    return int.from_bytes(bStr, byteorder='big')

def itob(num, s=0):
    if not s: return num.to_bytes(num//256+1, byteorder='big')
    else: return num.to_bytes(s, byteorder='big')


class DoubleDict(dict):
    '''
    Словарь такого типа позволяет отдавать как значение по ключу, так и ключ по значению.
    При небольшом размере словаря целесообразно использовать его зеркальную копию для ускорения поиска
    '''
    
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.mirrored = {v:k for k,v in self.items()}
    
    def __getitem__(self, *args, **kwargs):
        try:
            return dict.__getitem__(self, *args, **kwargs)
        except KeyError:
            try:
                return self.mirrored.__getitem__(*args, **kwargs)
            except KeyError:
                return b''


allFields = OrderedDict({
    'Queries': ('Name', 'Type', 'Class'),
    'Answers': ('Name', 'Type', 'Class', 'TTL', 'Data length', 'Address'),
    'Authoritative NS': ('Name', 'Type', 'Class', 'TTL', 'Data length', 'Name Server'),
    'Additional records': ('Name', 'Type', 'Class', 'TTL', 'Data length', 'Address', 'CNAME')
})

fieldGroups = list(allFields.keys())

class DNSPacket:

    def __init__(self, rawdata):
        '''при инициализации с байтовым аргументом пакет парсится в self.__records'''
        self.__binarydata = rawdata
        self.classes = {b'\x00\x01': 'IN'}
        self.types = DoubleDict({b'\x00\x01': 'A',
                      b'\x00\x02': 'NS',
                      b'\x00\x05': 'CNAME',
                      b'\x00\x06': 'SOA',
                      b'\x00\x0c': 'PTR',
                      b'\x00\x0f': 'MX',
                      b'\x00\x1c': 'AAAA',
                      b'\x00\xfc': 'AXFR'})
        
        self.__records = {g:[] for g in fieldGroups}
        self.readOffs = 0
        self.offsets = {}
        
        if type(self.__binarydata) != bytes:
            self.__createPacket()
        self.__parseAll()
            
    @staticmethod
    def strEncode(bStr) -> bytes:
        '''кодирует строку в формат (длина_до_точки)+зона1+(длина_до_точки)+зона2...\x00'''
        if type(bStr) == str:
            bStr = bStr.split('.')
        return b''.join(itob(len(i))+i.encode('ascii') for i in bStr) + b'\x00'
    
    def __createPacket(self):
        '''при инициализации объекта с аргументами в виде 'имя', 'тип', 'класс' пакет сериализуется в бинарную строку'''
        
        global packet_id
        self.__binarydata = b''.join([
            itob(packet_id, 2), #transaction ID
            b'\x00\x10', #no flags
            b'\x00\x01', #only questions
            b'\x00\x00'*3, #no answers
            self.strEncode(self.__binarydata[0]),
            self.types[self.__binarydata[1]],
            b'\x00\x01'
        ])
        packet_id += 1

    def removeField(self, dkey):
        self.__records[dkey].clear()

    def addField(self, dkey, vname=None, vtype=None, data=None, ttl=86400, dlen=4):
        '''добавляет параметры в self.__records[dkey]'''
        if dkey == 'Answers':
            if vname == None:
                self.__records[dkey].append(data)
            self.to_app = {'Name': vname,
                           'Type': vtype, 
                           'Class': 'IN',
                           'TTL': ttl,
                           'Data length': dlen}
            if vtype == 'A':
                self.to_app['Address'] = data
            elif vtype == 'CNAME':
                self.to_app['CNAME'] = data
            self.__records[dkey].append(self.to_app)
        else:
            self.__records[dkey] = data

    def setPointers(self, bstr) -> str:
        '''расстановка указателей на строки в бинарном представлении пакета, ищет в дополнительном буфере (не в основном!)'''
        self.pbdata = bytes(self.bindata)
        for i in range(len(bstr)):
            self.text = self.strEncode(bstr[i:])
            if self.text in self.offsets.keys() and self.text in self.pbdata:
                return self.strEncode(bstr[:i])[:-1] + self.offsets[self.text]
            self.doffs = self.pbdata.find(self.text)
            if self.doffs != -1:
                #print('bstr:', self.itob(0xc000 | self.doffs, 2), i, bstr[:i])
                self.offsets[self.text] = itob(0xc000 | self.doffs, 2)
                return self.strEncode(bstr[:i])[:-1] + self.offsets[self.text]
        return self.strEncode(bstr)
        
    def serialize(self, indict=None):
        '''сериализует словарь в бинарную строку'''
        if indict == None:
            indict = self.__records
        self.lens = [len(indict[i]) for i in fieldGroups]
        self.bindata = bytearray(b''.join([
            indict['ID'],
            indict['Flags']
        ]))
        self.bindata.extend(b''.join(itob(i, 2) for i in self.lens))
        print(self.bindata)
        self.lens = self.lens.__iter__()
        for fieldgroup in fieldGroups:
            print(fieldgroup)
            for counter in range(self.lens.__next__()):
                print(counter)
                for field in allFields[fieldgroup]:
                    try:
                        self.itm = indict[fieldgroup][counter][field]
                    except:
                        continue
                    print(field, self.itm)
                    if field == 'Type':
                        self.itm = self.types[self.itm]
                    elif field == 'Class':
                        self.itm = b'\x00\x01'
                    elif field == 'TTL':
                        self.itm = itob(self.itm, 4)
                    elif field == 'Data length':
                        self.itm = itob(self.itm, 2)
                    elif field == 'Address':
                        if '.' in self.itm:
                            self.itm = b''.join(map(lambda a: itob(int(a), 1), self.itm.split('.')))
                        elif ':' in self.itm:
                            self.itm = b''.join(map(lambda a: itob(int(a, 16), 1), self.itm.split(':')))  
                    elif field == 'Name' or field == 'Name server' or field == 'CNAME':
                        #print(self.itm, self.bindata)
                        self.itm = self.setPointers(self.itm.split('.'))
                    self.bindata.extend(self.itm)
        self.__binarydata = bytes(self.bindata)
        
    def __parseAll(self):
        self.hdrs = [None]*6
        try:
            for i in range(len(self.hdrs)):
                self.hdrs[i] = self.__substr(2)
                if i>=2:
                    self.hdrs[i] = btoi(self.hdrs[i])
            self.__records['ID'] = self.hdrs[0]
            self.__records['Flags'] = self.hdrs[1]
            self.hdrs = self.hdrs[2:].__iter__()
            for fgroup in fieldGroups:
                for _ in range(self.hdrs.__next__()):
                    self.fields = {}
                    self.fields['Name'] = self.strDecode(self.__binarydata[self.readOffs:]).decode('ascii')
                    self.fields['Type'] = self.types[self.__substr(2)]
                    self.fields['Class'] = self.classes[self.__substr(2)]
                    if fgroup != 'Queries':
                        self.fields['TTL'] = btoi(self.__substr(4))
                        self.fields['Data length'] = btoi(self.__substr(2))
                        if fgroup == 'Authoritative NS':
                            self.fields['Name server'] = self.strDecode(self.__substr(self.fields['Data length']), move_carriage=False).decode('ascii')
                        else:
                            if self.fields['Type'] == 'CNAME':
                                self.fields['CNAME'] = self.strDecode(self.__substr(self.fields['Data length']), move_carriage=False).decode('ascii')
                            else:
                                if self.fields['Data length'] == 16:
                                    self.fields['Address'] = ':'.join(hex(i)[2:] for i in self.__substr(16))
                                else:
                                    self.fields['Address'] = '.'.join(str(i) for i in self.__substr(4))
                    self.__records[fgroup].append(self.fields)
                #print('FINALLY:', self.__binarydata[self.readOffs:])
        except ArithmeticError:
            traceback.print_exc()
            print('Error was in', self.readOffs)
            
    def __substr(self, sublen) -> str:
        '''как головка, читающая ленту: возвращается n следующих элементов строки'''
        self.sub = self.__binarydata[self.readOffs:self.readOffs+sublen]
        self.readOffs += sublen
        return self.sub
    
    def getItemByOffset(self, bStr) -> str:
        if bStr not in self.offsets.keys():
            self.offsets[bStr] = self.strDecode(self.__binarydata[btoi(bStr) & 0x3fff:], move_carriage=False)
        return self.offsets[bStr]

    def strDecode(self, bStr, move_carriage=True) -> bytes:
        '''парсит бинарную строку из пакета (с длинами до точек и указателями) в читабельную'''
        result = []
        ptr = None
        strlen = 0
        while ptr != 0:
            ptr = bStr[0]
            if ptr & 0xc0 == 0xc0:
                result.append(self.getItemByOffset(bStr[:2]))
                strlen += 2
                #print('PTR_SOLVE:', result)
                break
            strlen += ptr+1
            if ptr == 0:
                break
            result.append(bStr[1:ptr+1])
            bStr = bStr[ptr+1:]
        if move_carriage:
            self.readOffs += strlen
        return b'.'.join(result)

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
        return self.__binarydata
    
