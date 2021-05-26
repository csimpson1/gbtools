create or replace table operation(
	operation_id int auto_increment primary key,
	mnemonic char(12) not null,
	zero_flag char(5),
	subtract_flag char(5),
	half_carry_flag char(4),
	carry_flag char(4)
);
	
create or replace table operand(
	operand_id int auto_increment primary key,
	operand_name char(10) not null,
	size int not null
);

create or replace table opcode(
	opcode_id int auto_increment primary key,
	code char(6) not null,
	operation_id int not null,
	bytes int not null,
	cycles int not null,
	conditional_cycles int,
	
	constraint fk_operation
	foreign key(operation_id)
		references operation(operation_id)
);

create or replace table instruction(
	instruction_id int auto_increment primary key,
	opcode_id int not null,
	operand_id int,
	op_order int,
	op_immediate bool,
	op_action char(1),
	
	constraint fk_opcode
	foreign key(opcode_id)
		references opcode(opcode_id),
		
	constraint fk_operand
	foreign key(operand_id)
		references operand(operand_id)
);

create or replace view opcodes_v
as
select 
	o.code, 
	op.mnemonic, 
	o.bytes, 
	o.cycles, 
	o.conditional_cycles,  
	op.zero_flag, 
	op.subtract_flag, 
	op.half_carry_flag,
	op.carry_flag, 
	opa.operand_name,
	opa.`size`,
	i.op_action,
	i.op_order, 
	i.op_immediate 
from instruction i
left join opcode o on i.opcode_id = o.opcode_id
left join operation op on op.operation_id  = o.operation_id 
left join operand opa on i.operand_id = opa.operand_id
order by i.instruction_id, i.op_order; 

