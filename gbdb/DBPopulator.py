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
        
        self.connect()
        
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
        self.cur = cur
    
    def clean_up(self):
        self.cur.close()
        self.conn.close()
        
        
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
                    
                    
                    row = (name, bytes)
                
                    if row not in uniqueOperands:
                        uniqueOperands.append(row)
                
  
        print('finished getting operands')
        print('inserting values into operand table')
        self.cur.executemany('insert into operand (operand_name, size) values (?, ?)', uniqueOperands)
        self.conn.commit()
        print('done inserting')
        print('--------------------')
    
    
    def get_flag_actions(self):
        #Get all the unique combinations of actions and populate the flag_action table
        
        uniqueFlagActions = []
        
        for type in ['unprefixed', 'cbprefixed']:
            for code in self.opcodes[type]:
                flags = self.opcodes[type][code]['flags']
                flagAction = [flags['Z'], flags['N'], flags['H'], flags['C']]
                flagAction = tuple(['' if x == '-' else x for x in flagAction])
                
                if flagAction not in uniqueFlagActions:
                    uniqueFlagActions.append(flagAction)
        
        print('finished getting flag actions')
        print('inserting flag actions')
        self.cur.executemany("insert into flag_action (zero_flag, subtract_flag, half_carry_flag, carry_flag) values (?, ?, ?, ?)", uniqueFlagActions)
        self.conn.commit()
        print('done inserting')
        print('--------------------')    
        
    
    def get_operations(self):
        #Get the unique operations from the set of opcodes and populate the operation table
        
        getFlagsIDQuery = """
        select flag_action_id from flag_action
        where 
        zero_flag = ? and 
        subtract_flag = ? and
        half_carry_flag = ? and
        carry_flag = ?
        """
        uniqueOperations = []
        
        for type in ['unprefixed', 'cbprefixed']:
            for code in self.opcodes[type]:
                                    
                flags = self.opcodes[type][code]['flags']
                currentFlags = [flags['Z'], flags['N'], flags['H'], flags['C']]
                currentFlags = tuple(['' if x == '-' else x for x in currentFlags])
                
                self.cur.execute(getFlagsIDQuery, currentFlags)
                results = self.cur.fetchall()
                
                if len(results) > 1:
                    print(f"Error when fetching flags for operation {code} {self.opcodes[type][code]['mnemonic']}: multiple flag ids identified")
                    sys.exit(-1)
                    
                elif len(results) == 0:
                    print(f"Error when fetching flags for operation {code} {self.opcodes[type][code]['mnemonic']}: no flag ids identified")
                    sys.exit(-1)
                    
                else:
                    flagActionId = results[0][0]
                
                if type == 'cbprefixed':
                    name = code[0:2] + "CB" + code[2:]
                else:
                    name = code
                
                bytes = self.opcodes[type][code]['bytes']
                cycles = self.opcodes[type][code]['cycles'][0]
                mnemonic = self.opcodes[type][code]['mnemonic']
                
                try:
                    conditionalCycles = self.opcodes[type][code]['cycles'][1]
                
                except IndexError as e:
                    conditionalCycles = None
                
                operation = (name, mnemonic, bytes, cycles, conditionalCycles, flagActionId)
                
                if operation not in uniqueOperations:
                    uniqueOperations.append(operation)
                
                
        print('finished getting operations')
        print('inserting flag actions')
        self.cur.executemany("insert into operation (code, mnemonic, bytes, cycles, conditional_cycles, flag_action_id) values (?, ?, ?, ?, ?, ?)", uniqueOperations)
        self.conn.commit()
        print('done inserting')
        print('--------------------')  
                
                
                    
        print('finished getting operations') 
        print('inserting values into operation table')
        #self.cur.executemany("insert into operation (mnemonic, zero_flag, subtract_flag, half_carry_flag, carry_flag) values (?, ?, ?, ?, ?)", uniqueRows)
        #self.conn.commit()
        print('done inserting')
        print('--------------------')    
    
    def get_operand_actions(self):
        #Insert the values of special actions that can be taken on an operand post execution, like increment and decrement.
        #These are the only two values in this table, and I don't expect the GB CPU to change any time soon, so just hardcoding these
        
        operandActions = [
            ('+', "Increment operand after instruction executes"),
            ('-', "Decrement operand after instruction executes")
            ]
        
        print('done getting operand actions')
        print('inserting into operand_action table')
        self.cur.executemany('insert into operand_action (operand_action_symbol, operand_action_desc) values (?, ?)', operandActions)
        self.conn.commit()
        print('done inserting')
        
    def get_instructions(self):
        print('getting instructions')
        instructionsToInsert = []
        
        operationQuery = """
        select operation_id from operation
        where
        code=?
        """
        
        operandQuery = """
        select operand_id from operand
        where operand_name=?
        """
        
        operandActionQuery = """
        select operand_action_id, operand_action_symbol from operand_action
        """
        
        self.cur.execute(operandActionQuery)
        results = self.cur.fetchall()
        actionMapping = {}
        
        for action in results:
            if action[1] == '+':
                actionMapping['increment'] = action[0]
            elif action[1] == '-':
                actionMapping['decrement'] = action[0]
        
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
                
                self.cur.execute(operationQuery, (str(codeToSelect),))
                results = self.cur.fetchall()
                if len(results) > 1:
                    print(f"Error when finding identifier for {code}. Multiple IDs were found")
                    sys.exit(-1)
                elif len(results) == 0:
                    opcode = None
                    print(f"Error when finding identifier for {code}. No IDs found")
                    sys.exit(-1)
                else:
                    operationId = results[0][0]
                
                
                if not self.opcodes[type][code]['operands']:
                    instructionsToInsert.append((operationId, None, None, None, None))
                    
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
                                action = actionMapping['increment']
                            
                            elif 'decrement' in operand:
                                action = actionMapping['decrement']
                                
                            
                            
                        instructionsToInsert.append((operationId, operandId, operandCounter, immediate, action))
                        operandCounter += 1    
        #for line in instructionsToInsert:
        #    print(line)        
            
        print('done getting instruction linking')
        print('inserting into instruction table')
        self.cur.executemany('insert into instruction (operation_id, operand_id, op_order, op_immediate, operand_action_id) values (?, ?, ?, ?, ?)', instructionsToInsert)
        self.conn.commit()
        print('done inserting')
                        
                                
                        
                        
                

                
                    


if __name__ == '__main__':
    codes = DBPopulater()

    codes.get_operands()
    codes.get_flag_actions()
    codes.get_operations()
    codes.get_operand_actions()
    codes.get_instructions()
    codes.clean_up()
    
    