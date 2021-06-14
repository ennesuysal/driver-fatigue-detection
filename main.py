import cv2
import slope
import perclos
import yawn
import time
import vlc
import os

def main():
    short_flag_eye = 0
    short_start_eye = time.time()
    short_flag_slope = 0
    short_start_slope = time.time()
    general_start = time.time()
    yawn_fatigue_flag = 0
    music_flag_eye = 0
    music_flag_slope = 0
    music_flag_yawn = 0
    yawn_alarm_timer = 0
    perclos_value = 0
    isYawning = 0
    p = vlc.MediaPlayer("alarm.mp3")
    detectSlope = slope.DetectSlope()
    pCLOS = perclos.perclos()
    vCap = cv2.VideoCapture(0)
    while True:
        ret, frame = vCap.read()
        frame = cv2.resize(frame, (640,480))
        if ret == True:
            #Detect Slope
            detectSlope.load_img(frame)
            angle = detectSlope.find_slop()
            cv2.putText(frame, "{:.2f} DERECE".format(angle), (frame.shape[1]-390, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            if abs(angle) < 12:
                cv2.putText(frame, "Duz", (frame.shape[1]-350, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), 2)
            else:
                cv2.putText(frame, "Egik", (frame.shape[1]-350, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), 2)

            # Yawn
            yawn.yawnDetect(frame)
            if yawn.mar > 0.38:
                isYawning = 1
            else:
                isYawning = 0


            #Calculate Perclos
            pCLOS.load_img(frame)
            ear = pCLOS.calc_ear()
            cv2.putText(frame, "EAR: {:.2f}".format(ear), (frame.shape[1]-150, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            if ear >= pCLOS.EYE_AR_THRESH:
                cv2.putText(frame, "ACIK", (frame.shape[1]-130, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                cv2.putText(frame, "KAPALI", (frame.shape[1]-130, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # 10 saniyelik dilim dolduğunda perclosu hesapla
            if time.time() - general_start > 10:
                perclos_value = pCLOS.calc_perclos()

            cv2.putText(frame, "PERCLOS: {:.2f}".format(perclos_value), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            if perclos_value >= 80:
                cv2.putText(frame, "Yorgun", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                cv2.putText(frame, "Yorgun Degil", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            if ear >= 0.23 or isYawning == 1:
                music_flag_eye = 0
                if music_flag_yawn == 0 and music_flag_slope == 0:
                    p.stop()
                short_flag_eye = 0
            else:
                if short_flag_eye == 0:
                    short_start_eye = time.time()
                    short_flag_eye = 1
                else:
                    end = time.time()
                    if end - short_start_eye >= 2:
                        if music_flag_eye == 0 and music_flag_slope == 0:
                            p.play()
                            music_flag_eye = 1

            if music_flag_eye == 1:
                cv2.putText(frame, "UYARI!".format(ear), (frame.shape[1] - 150, 110),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            if angle <= 15:
                short_flag_slope = 0
                music_flag_slope = 0
                if music_flag_eye == 0 and music_flag_yawn == 0:
                    p.stop()
            else:
                if short_flag_slope == 0:
                    short_start_slope = time.time()
                    short_flag_slope = 1
                else:
                    end = time.time()
                    if end - short_start_slope >= 4:
                        if music_flag_slope == 0 and music_flag_eye == 0:
                            p.play()
                            music_flag_slope=1
            if music_flag_slope == 1:
                cv2.putText(frame, "UYARI!".format(ear), (frame.shape[1] - 150, 110),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            if type(pCLOS.leftEye) is not int or type(pCLOS.rightEye) is not int:
                leftEyeHull = cv2.convexHull(pCLOS.leftEye)
                rightEyeHull = cv2.convexHull(pCLOS.rightEye)
                cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
                cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

            timer_end = time.time()
            if timer_end - general_start >= 10:
                if yawn.yawn_counter > 1 and perclos_value >= 50 and perclos_value < 80:
                    yawn_fatigue_flag = 1
                    if music_flag_slope == 0 and music_flag_eye == 0:
                        p.play()
                        music_flag_yawn = 1
                        yawn_alarm_timer = time.time()
                else:
                    music_flag_yawn = 0
                    yawn_fatigue_flag = 0
                    if music_flag_eye == 0 and music_flag_slope == 0:
                        p.stop()
                yawn.yawn_counter = 0
                general_start = time.time()

            if yawn_fatigue_flag == 1:
                cv2.putText(frame, "ERKEN UYARI!!".format(ear), (frame.shape[1] - 150, 110),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            if timer_end - yawn_alarm_timer >= 3:
                music_flag_yawn = 0
                yawn_fatigue_flag = 0
                if music_flag_eye == 0 and music_flag_slope == 0:
                    p.stop()


        #Show Frame
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    cv2.destroyAllWindows()
    vCap.release()


if __name__ == '__main__':
    main()
