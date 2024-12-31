F1:: 
{
    StopLoop := False  ; Initialize the stop flag

    Loop 
    {
        ; Perform ImageSearch with a tolerance level of 10
        ImageSearch, FoundX, FoundY, 0, 0, A_ScreenWidth, A_ScreenHeight, *10 Wabbajack_UZFcbw8ipK.png
        
        ; Check if ImageSearch was successful
        if (ErrorLevel)  ; ErrorLevel is non-zero if the image was not found
        {
            ; Optionally, show a message if image is not found
            ; MsgBox, Image not found!
            continue  ; Continue to the next iteration if the image isn't found
        }

        ; If the image is found, click on it
        MouseClick, left, %FoundX%, %FoundY%
	Sleep, 500
	MouseMove, 0, 0
        Sleep, 4000  ; Wait for 4 seconds

        ; Break the loop if StopLoop is True
        if (StopLoop)
        {
            break
        }
    }
}
return

Esc:: 
{
    StopLoop := True  ; Set the stop flag to true when Escape is pressed
    return
}