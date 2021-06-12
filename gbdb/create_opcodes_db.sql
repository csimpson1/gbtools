  /*********************/
 /* Database creation */
/*********************/

drop database MDB_GBDB;
  
create or replace database MDB_GBDB;
use MDB_GBDB;


  /******************/
 /* Table Creation */
/******************/

create or replace table operand(
	operand_id   int      auto_increment primary key,
	operand_name char(10) not null,
	size         int      not null
);

create or replace table flag_action(
	flag_action_id int auto_increment primary key,
	zero_flag       char(1),
	subtract_flag   char(1),
	half_carry_flag char(1),
	carry_flag      char(1)
);

create or replace table operand_action(
	operand_action_id int auto_increment primary key,
	operand_action_symbol char(1),
	operand_action_desc char(50)
);


create or replace table operation(
	operation_id int auto_increment primary key,
	code char(6) not null,
	mnemonic char(10) not null,
	flag_action_id int not null,
	bytes int not null,
	cycles int not null,
	conditional_cycles int,
	
	constraint fk_operation_flag_action
	foreign key(flag_action_id)
		references flag_action(flag_action_id)
);

create or replace table instruction(
	instruction_id int auto_increment primary key,
	operation_id int not null,
	operand_id int,
	op_order int,
	op_immediate bool,
	operand_action_id int,
	
	constraint fk_instruction_operation
	foreign key(operation_id)
		references operation(operation_id),
		
	constraint fk_instruction_operand
	foreign key(operand_id)
		references operand(operand_id),
		
	constraint fk_instruction_operand_action
	foreign key(operand_action_id)
		references operand_action(operand_action_id)
);

  /*****************/
 /* View Creation */
/*****************/

create or replace view opcodes_v
as
select 
	o.code, 
	o.mnemonic, 
	o.bytes, 
	o.cycles, 
	o.conditional_cycles,  
	fa.zero_flag, 
	fa.subtract_flag, 
	fa.half_carry_flag,
	fa.carry_flag, 
	opa.operand_name,
	opa.`size`,
	oac.operand_action_symbol,
	i.op_order, 
	i.op_immediate 
from instruction i
join operation o on i.operation_id = o.operation_id
left join operand opa on i.operand_id = opa.operand_id 
join flag_action fa on o.flag_action_id  = fa.flag_action_id
left join operand_action oac on i.operand_action_id  = oac.operand_action_id
order by i.instruction_id, i.op_order; 

