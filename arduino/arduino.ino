int coi = 5;
void setup() {
  Serial.begin(9600);
  pinMode(coi, OUTPUT);
}
void loop() {
  String receivedString = "";  // Chuỗi để lưu trữ dữ liệu từ cổng serial

  // Đọc chuỗi mới nhất
  while (Serial.available() > 0) {
    char c = Serial.read();  // Đọc một ký tự từ cổng serial
    receivedString += c;     // Thêm ký tự vào chuỗi
    delay(2);                // Đợi một chút để nhận toàn bộ dữ liệu
  }
  if (receivedString.length() > 0) {
    if (receivedString == "true") {
      digitalWrite(coi, HIGH);
    }
  }
}