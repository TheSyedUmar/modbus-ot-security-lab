PROGRAM tank
  VAR
    level AT %QW100 : INT;
    pump  AT %QX100.0 : BOOL;
  END_VAR

  IF level < 20 THEN
    pump := TRUE;
  ELSIF level > 80 THEN
    pump := FALSE;
  END_IF;
END_PROGRAM

CONFIGURATION Config0
  RESOURCE Res0 ON PLC
    TASK task0(INTERVAL := T#20ms, PRIORITY := 0);
    PROGRAM instance0 WITH task0 : tank;
  END_RESOURCE
END_CONFIGURATION
