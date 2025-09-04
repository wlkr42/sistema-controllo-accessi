#include "LoadCrt288lib.h"

static void *  hModule  = NULL;
static bool returnValue = false;

Crt288_drv g_crt288_drv;

bool LoadMyLib(const char lpDllPath[], char ErrorInfo[])
{
	//定义变量
	returnValue = false;
	//判断参数
	if(ErrorInfo == NULL)
	{
		goto ExitLine;
	}
	//加载动态库
	if(hModule)
	{
		returnValue = true;
		goto ExitLine;
	}

	hModule = dlopen(lpDllPath, RTLD_LAZY);
	if(hModule == NULL)
	{
		sprintf(ErrorInfo, "加载传入:%s失败!",lpDllPath);
		//加载传入路径失败，再加载一次当前路径默认DLL
		hModule = dlopen("./crt_288x_ur.so", RTLD_LAZY);
		if(hModule == NULL)
		{
			sprintf(ErrorInfo, "%s--默认路径加载也失败!", ErrorInfo);
			goto ExitLine;
		}
	}

	//******************************************************************************************************************
	//加载CRT288x_OpenConnection
	g_crt288_drv.CRT288x_OpenConnection = (pCRT288x_OpenConnection)dlsym(hModule, "CRT288x_OpenConnection");
	if(!g_crt288_drv.CRT288x_OpenConnection)
	{
		sprintf(ErrorInfo, "加载'CRT288x_OpenConnection'失败!");
		goto ExitLine;
	}
	
	//******************************************************************************************************************
	//加载CRT288x_CloseConnection
	g_crt288_drv.CRT288x_CloseConnection = (pCRT288x_CloseConnection)dlsym(hModule, "CRT288x_CloseConnection");
	if(!g_crt288_drv.CRT288x_CloseConnection)
	{
		sprintf(ErrorInfo, "加载'CRT288x_CloseConnection'失败!");
		goto ExitLine;
	}
	
	//******************************************************************************************************************
	//加载CRT288x_ExeCommand
	g_crt288_drv.CRT288x_ExeCommand = (pCRT288x_ExeCommand)dlsym(hModule, "CRT288x_ExeCommand");
	if(!g_crt288_drv.CRT288x_ExeCommand)
	{
		sprintf(ErrorInfo, "加载'CRT288x_ExeCommand'失败!");
		goto ExitLine;
	}
	
	//******************************************************************************************************************
	//加载CRT288x_InitDev
	g_crt288_drv.CRT288x_InitDev = (pCRT288x_InitDev)dlsym(hModule, "CRT288x_InitDev");
	if(!g_crt288_drv.CRT288x_InitDev)
	{
		sprintf(ErrorInfo, "加载'CRT288x_InitDev'失败!");
		goto ExitLine;
	}
	
	//******************************************************************************************************************
	//加载CRT288x_GetCardStatus
	g_crt288_drv.CRT288x_GetCardStatus = (pCRT288x_GetCardStatus)dlsym(hModule, "CRT288x_GetCardStatus");
	if(!g_crt288_drv.CRT288x_GetCardStatus)
	{
		sprintf(ErrorInfo, "加载'CRT288x_GetCardStatus'失败!");
		goto ExitLine;
	}

	//******************************************************************************************************************
	//加载CRT288x_GetLockStatus
	g_crt288_drv.CRT288x_GetLockStatus = (pCRT288x_GetLockStatus)dlsym(hModule, "CRT288x_GetLockStatus");
	if(!g_crt288_drv.CRT288x_GetLockStatus)
	{
		sprintf(ErrorInfo, "加载'CRT288x_GetLockStatus'失败!");
		goto ExitLine;
	}
	
	//******************************************************************************************************************
	//加载CRT288x_LockedProcess
	g_crt288_drv.CRT288x_LockedProcess = (pCRT288x_LockedProcess)dlsym(hModule, "CRT288x_LockedProcess");
	if(!g_crt288_drv.CRT288x_LockedProcess)
	{
		sprintf(ErrorInfo, "加载'CRT288x_LockedProcess'失败!");
		goto ExitLine;
	}

	//******************************************************************************************************************
	//加载CRT288x_LEDProcess
	g_crt288_drv.CRT288x_LEDProcess = (pCRT288x_LEDProcess)dlsym(hModule, "CRT288x_LEDProcess");
	if(!g_crt288_drv.CRT288x_LEDProcess)
	{
		sprintf(ErrorInfo, "加载'CRT288x_LEDProcess'失败!");
		goto ExitLine;
	}
	
	//******************************************************************************************************************
	//加载CRT288x_SetLEDFlashTime
	g_crt288_drv.CRT288x_SetLEDFlashTime = (pCRT288x_SetLEDFlashTime)dlsym(hModule, "CRT288x_SetLEDFlashTime");
	if(!g_crt288_drv.CRT288x_SetLEDFlashTime)
	{
		sprintf(ErrorInfo, "加载'CRT288x_SetLEDFlashTime'失败!");
		goto ExitLine;
	}
	
	
	//******************************************************************************************************************
	//加载CRT288x_SetReaderMagType
	g_crt288_drv.CRT288x_SetReaderMagType = (pCRT288x_SetReaderMagType)dlsym(hModule, "CRT288x_SetReaderMagType");
	if(!g_crt288_drv.CRT288x_SetReaderMagType)
	{
		sprintf(ErrorInfo, "加载'CRT288x_SetReaderMagType'失败!");
		goto ExitLine;
	}
	
	//******************************************************************************************************************
	//加载CRT288x_ReadTrack
	g_crt288_drv.CRT288x_ReadTrack = (pCRT288x_ReadTrack)dlsym(hModule, "CRT288x_ReadTrack");
	if(!g_crt288_drv.CRT288x_ReadTrack)
	{
		sprintf(ErrorInfo, "加载'CRT288x_ReadTrack'失败!");
		goto ExitLine;
	}
		
	//******************************************************************************************************************
	//加载CRT288x_ReadAllTracks
	g_crt288_drv.CRT288x_ReadAllTracks = (pCRT288x_ReadAllTracks)dlsym(hModule, "CRT288x_ReadAllTracks");
	if(!g_crt288_drv.CRT288x_ReadAllTracks)
	{
		sprintf(ErrorInfo, "加载'CRT288x_ReadAllTracks'失败!");
		goto ExitLine;
	}
	
	//******************************************************************************************************************
	//加载CRT288x_ClearTrackData
	g_crt288_drv.CRT288x_ClearTrackData = (pCRT288x_ClearTrackData)dlsym(hModule, "CRT288x_ClearTrackData");
	if(!g_crt288_drv.CRT288x_ClearTrackData)
	{
		sprintf(ErrorInfo, "加载'CRT288x_ClearTrackData'失败!");
		goto ExitLine;
	}

	//******************************************************************************************************************
	//加载CRT288x_GetICType
	g_crt288_drv.CRT288x_GetICType = (pCRT288x_GetICType)dlsym(hModule, "CRT288x_GetICType");
	if(!g_crt288_drv.CRT288x_GetICType)
	{
		sprintf(ErrorInfo, "加载'CRT288x_GetICType'失败!");
		goto ExitLine;
	}

	//******************************************************************************************************************
	//加载CRT288x_GetRFType
	g_crt288_drv.CRT288x_GetRFType = (pCRT288x_GetRFType)dlsym(hModule, "CRT288x_GetRFType");
	if(!g_crt288_drv.CRT288x_GetRFType)
	{
		sprintf(ErrorInfo, "加载'CRT288x_GetRFType'失败!");
		goto ExitLine;
	}
	
	//******************************************************************************************************************
	//加载CRT288x_ChipPower
	g_crt288_drv.CRT288x_ChipPower = (pCRT288x_ChipPower)dlsym(hModule, "CRT288x_ChipPower");
	if(!g_crt288_drv.CRT288x_ChipPower)
	{
		sprintf(ErrorInfo, "加载'CRT288x_ChipPower'失败!");
		goto ExitLine;
	}

	//******************************************************************************************************************
	//加载CRT288x_ChipIO
	g_crt288_drv.CRT288x_ChipIO = (pCRT288x_ChipIO)dlsym(hModule, "CRT288x_ChipIO");
	if(!g_crt288_drv.CRT288x_ChipIO)
	{
		sprintf(ErrorInfo, "加载'CRT288x_ChipIO'失败!");
		goto ExitLine;
	}

	//******************************************************************************************************************
	//加载CRT288x_GetCardActiveStatus
	g_crt288_drv.CRT288x_GetCardActiveStatus = (pCRT288x_GetCardActiveStatus)dlsym(hModule, "CRT288x_GetCardActiveStatus");
	if(!g_crt288_drv.CRT288x_GetCardActiveStatus)
	{
		sprintf(ErrorInfo, "加载'CRT288x_GetCardActiveStatus'失败!");
		goto ExitLine;
	}
	
	//******************************************************************************************************************
	//加载CRT288x_SAMSlotChange
	g_crt288_drv.CRT288x_SAMSlotChange = (pCRT288x_SAMSlotChange)dlsym(hModule, "CRT288x_SAMSlotChange");
	if(!g_crt288_drv.CRT288x_SAMSlotChange)
	{
		sprintf(ErrorInfo, "加载'CRT288x_SAMSlotChange'失败!");
		goto ExitLine;
	}	

	//******************************************************************************************************************
	//加载CRT288x_SetVcc
	g_crt288_drv.CRT288x_SetVcc = (pCRT288x_SetVcc)dlsym(hModule, "CRT288x_SetVcc");
	if(!g_crt288_drv.CRT288x_SetVcc)
	{
		sprintf(ErrorInfo, "加载'CRT288x_SetVcc'失败!");
		goto ExitLine;
	}

//******************************************************************************************************************
	//加载CRT288x_SL4442CheckPasswd
	g_crt288_drv.CRT288x_SL4442CheckPasswd = (pCRT288x_SL4442CheckPasswd)dlsym(hModule, "CRT288x_SL4442CheckPasswd");
	if(!g_crt288_drv.CRT288x_SL4442CheckPasswd)
	{
		sprintf(ErrorInfo, "加载'CRT288x_SL4442CheckPasswd'失败!");
		goto ExitLine;
	}

//******************************************************************************************************************
	//加载CRT288x_SL4442Process
	g_crt288_drv.CRT288x_SL4442Process = (pCRT288x_SL4442Process)dlsym(hModule, "CRT288x_SL4442Process");
	if(!g_crt288_drv.CRT288x_SL4442Process)
	{
		sprintf(ErrorInfo, "加载'CRT288x_SL4442Process'失败!");
		goto ExitLine;
	}

//******************************************************************************************************************
	//加载CRT288x_SL4428CheckPasswd
	g_crt288_drv.CRT288x_SL4428CheckPasswd = (pCRT288x_SL4428CheckPasswd)dlsym(hModule, "CRT288x_SL4428CheckPasswd");
	if(!g_crt288_drv.CRT288x_SL4428CheckPasswd)
	{
		sprintf(ErrorInfo, "加载'CRT288x_SL4428CheckPasswd'失败!");
		goto ExitLine;
	}

//******************************************************************************************************************
	//加载CRT288x_SL4428Process
	g_crt288_drv.CRT288x_SL4428Process = (pCRT288x_SL4428Process)dlsym(hModule, "CRT288x_SL4428Process");
	if(!g_crt288_drv.CRT288x_SL4428Process)
	{
		sprintf(ErrorInfo, "加载'CRT288x_SL4428Process'失败!");
		goto ExitLine;
	}

//******************************************************************************************************************
	//加载CRT288x_24CxProcess
	g_crt288_drv.CRT288x_24CxProcess = (pCRT288x_24CxProcess)dlsym(hModule, "CRT288x_24CxProcess");
	if(!g_crt288_drv.CRT288x_24CxProcess)
	{
		sprintf(ErrorInfo, "加载'CRT288x_24CxProcess'失败!");
		goto ExitLine;
	}

//******************************************************************************************************************
	//加载CRT288x_MifareKeyProcess
	g_crt288_drv.CRT288x_MifareKeyProcess = (pCRT288x_MifareKeyProcess)dlsym(hModule, "CRT288x_MifareKeyProcess");
	if(!g_crt288_drv.CRT288x_MifareKeyProcess)
	{
		sprintf(ErrorInfo, "加载'CRT288x_MifareKeyProcess'失败!");
		goto ExitLine;
	}

//******************************************************************************************************************
	//加载CRT288x_MifareCardProcess
	g_crt288_drv.CRT288x_MifareCardProcess = (pCRT288x_MifareCardProcess)dlsym(hModule, "CRT288x_MifareCardProcess");
	if(!g_crt288_drv.CRT288x_MifareCardProcess)
	{
		sprintf(ErrorInfo, "加载'CRT288x_MifareCardProcess'失败!");
		goto ExitLine;
	}

//******************************************************************************************************************
	//加载CRT288C_GetHidCardNums
	g_crt288_drv.CRT288C_GetHidCardNums = (pCRT288C_GetHidCardNums)dlsym(hModule, "CRT288C_GetHidCardNums");
	if(!g_crt288_drv.CRT288C_GetHidCardNums)
	{
		sprintf(ErrorInfo, "加载'CRT288C_GetHidCardNums'失败!");
		goto ExitLine;
	}


	
	returnValue = true;

ExitLine:
	if(!returnValue && hModule){
		dlclose(hModule);
		hModule = NULL;
	}
	return returnValue;
}



int UnLoadMyLib()
{
	if(hModule){
		dlclose(hModule);
	}
	hModule = NULL;
	
	return 0;
}
