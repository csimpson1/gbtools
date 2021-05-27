from collections import Counter as count
import json
import mariadb
import requests
import sys



class DBPopulater:
    
    def __init__(self):
        cmdRefUrl='https://gbdev.io/gb-opcodes/Opcodes.json'
        refPage = requests.get(cmdRefUrl)
        #print(refPage.text)
        self.opcodes = json.loads(refPage.text)
        self.cur = self.connect()
        
    def connect(self):
        try:
            self.conn = mariadb.connect(
                user='root',
                host='localhost',
                port=3306,
                database='MDB_GBDB'
                )
            
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(-1)
        
        cur = self.conn.cursor()
        print("connected!")
        return cur
    
    
    def get_operations(self):
        #Get the unique operations from the set of opcodes and populate the operation table
        
        uniqueRows = []
        
        for type in ['unprefixed', 'cbprefixed']:
            for code in self.opcodes[type]:
                #print(self.opcodes[type])
                opcode = self.opcodes[type][code]
                row = [opcode['mnemonic'], opcode['flags']['Z'], opcode['flags']['N'], opcode['flags']['H'], opcode['flags']['C']]
                row = tuple(['' if x == '-' else x for x in row])

                if row not in uniqueRows:
                    uniqueRows.append(row)
                    
        print('finished getting operations') 
        print('inserting values into operation table')
        self.cur.executemany("insert into operation (mnemonic, zero_flag, subtract_flag, half_carry_flag, carry_flag) values (?, ?, ?, ?, ?)", uniqueRows)
        self.conn.commit()
        print('done inserting')
        print('--------------------')
        
        
    def get_operands(self):
        
        uniqueOperands = []
        
        for type in ['unprefixed', 'cbprefixed']:
            for code in self.opcodes[type]:
                for operand in self.opcodes[type][code]['operands']:
                    name = operand['name']
                    if 'bytes' in operand:
                        bytes = operand['bytes']
                
                    else:
                        bytes = 0
                    
                    # Dealing with special actions on operands    
                    """
                    action = ""
                    
                    if 'increment' in operand:
                        action = "+"
                    
                    elif 'decrement' in operand:
                        action = "-"
                    
                    """
                    
                    row = (name, bytes)
                
                    if row not in uniqueOperands:
                        uniqueOperands.append(row)
                
  
        print('finished getting operands')
        print('inserting values into operand table')
        self.cur.executemany('insert into operand (operand_name, size) values (?, ?)', uniqueOperands)
        self.conn.commit()
        print('done inserting')
        print('--------------------')
    
    
    def get_opcodes(self):
        print('getting opcodes')
        codesToInsert = []
        
        query = """
        select operation_id from operation 
        where
        mnemonic = ? and
        zero_flag = ? and
        subtract_flag = ? and
        half_carry_flag = ? and
        carry_flag = ?
        """

        for type in ['unprefixed', 'cbprefixed']:
            for code in self.opcodes[type]:
                opcode = self.opcodes[type][code]
                
                if type == 'cbprefixed':
                    name = code[0:2] + "CB" + code[2:]
                else:
                    name = code
                
                bytes = self.opcodes[type][code]['bytes']
                cycles = self.opcodes[type][code]['cycles'][0]

                
                try:
                    conditionalCycles = self.opcodes[type][code]['cycles'][1]
                
                except IndexError as e:
                    conditionalCycles = None
                    
                #Find the operation id
                # The linkage needs to be performed based on the flags. Different operations have different 
                # flag actions
                
                identifier = [opcode['mnemonic'], opcode['flags']['Z'], opcode['flags']['N'], opcode['flags']['H'], opcode['flags']['C']]
                identifier = tuple(['' if x == '-' else x for x in identifier])
                
                self.cur.execute(query, identifier)
                results = self.cur.fetchall()
                
                operationId = None
                if len(results) > 1:
                    print(f"Error when finding identifier for {name} {opcode['mnemonic']}. Multiple operation ids identified.")
                    sys.exit(-1)
                
                elif len(results) == 0:
                    print(f"Error when finding identifier for {name} {opcode['mnemonic']}. No Matching operation found")
                else:
                        operationId = results[0][0]
                

                values = (name, operationId, bytes, cycles, conditionalCycles)
                codesToInsert.append(values)
        
        print('done getting opcodes')
        #DEBUG
        print('inserting opcodes into opcode table')
        self.cur.executemany("insert into opcode (code, operation_id, bytes, cycles, conditional_cycles) values (?,?,?,?,?)", codesToInsert)
        self.conn.commit()
        print('done inserting')
        print('--------------------')
        
        
    def get_instructions(self):
        print('getting instructions')
        instructionsToInsert = []
        
        opcodeQuery = """
        select opcode_id from opcode
        where
        code=?
        """
        
        operandQuery = """
        select operand_id from operand
        where operand_name=?
        """
        
        for type in ['unprefixed', 'cbprefixed']:
    
            
            for code in self.opcodes[type]:
                # Get the opcode id
                
                if type == 'cbprefixed':
                    #Add in the CB prefix
                    #Differentiate the prefixed opcode from the code variable
                    #Code is still being used to reference an element in the opcodes JSON,
                    #but might be incorrect when we select from the DB
                    codeToSelect = '0xCB' + code[2:]
                else:
                     codeToSelect = code
                
                self.cur.execute(opcodeQuery, (str(codeToSelect),))
                results = self.cur.fetchall()
                if len(results) > 1:
                    print(f"Error when finding identifier for {code}. Multiple IDs {opcodeId}, {test} were found")
                    sys.exit(-1)
                elif len(results) == 0:
                    opcode = None
                    print(f"Error when finding identifier for {code}. No IDs found")
                    sys.exit(-1)
                else:
                    opcodeId = results[0][0]
                
                
                if not self.opcodes[type][code]['operands']:
                    instructionsToInsert.append((opcodeId, None, None, None, None))
                    
                else:
                    operandCounter = 1
                    for operand in self.opcodes[type][code]['operands']:
                        name = operand['name']
                        #print(name)
                        # Get the operand id
                        self.cur.execute(operandQuery, (name,))
                        results = self.cur.fetchall()
                        
                        operandId = None
                        immediate = None
                        if len(results) > 1:
                            print(f"Error when finding identifier for {name}. Multiple IDs were found")
                            sys.exit(-1)
                        
                        elif len(results) == 0:
                            pass
                        
                        else:
                            operandId = results[0][0]
                            immediate = operand['immediate']
                            
                            #Handling the case when there is an additional action to perform on an operand
                            #such as incrementing it after it is accessed
                            action = None
                            
                            if 'increment' in operand:
                                action = '+'
                            
                            elif 'decrement' in operand:
                                action = '-'
                                
                            
                            
                        instructionsToInsert.append((opcodeId, operandId, operandCounter, immediate, action))
                        operandCounter += 1    
                
        print('done getting instruction linking')
        print('inserting into instruction table')
        self.cur.executemany('insert into instruction (opcode_id, operand_id, op_order, op_immediate, op_action) values (?, ?, ?, ?, ?)', instructionsToInsert)
        self.conn.commit()
        print('done inserting')
                        
                                
                        
                        
                

                
                    


if __name__ == '__main__':
    codes = DBPopulater()

    codes.get_operations()
    codes.get_operands()
    codes.get_opcodes()
    codes.get_instructions()
    
    
