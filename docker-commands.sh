#!/bin/bash

echo "=========================================="
echo "Soru Kategorizer Docker Komutları"
echo "=========================================="

# Docker imajını oluştur
echo "1. Docker imajını oluşturuyor..."
docker build -t question-categorizer .

echo ""
echo "2. Docker container'ı çalıştırıyor..."
# Container'ı çalıştır
docker run -d \
  --name categorizer-app \
  -p 5002:5002 \
  question-categorizer

echo ""
echo "3. Container durumunu kontrol ediyor..."
sleep 5
docker ps | grep categorizer

echo ""
echo "4. API health check yapıyor..."
curl -f http://localhost:5002/health || echo "Health check başarısız"

echo ""
echo "5. Test sorusu gönderiyoo..."
curl -X POST http://localhost:5002/categorize \
  -H "Content-Type: application/json" \
  -d '{"question": "Bu ürün orijinal mi?"}' \
  || echo "Test başarısız"

echo ""
echo "=========================================="
echo "Faydalı Docker Komutları:"
echo "=========================================="
echo "Container loglarını görmek için:"
echo "  docker logs categorizer-app"
echo ""
echo "Container'a bağlanmak için:"
echo "  docker exec -it categorizer-app bash"
echo ""
echo "Container'ı durdurmak için:"
echo "  docker stop categorizer-app"
echo ""
echo "Container'ı yeniden başlatmak için:"
echo "  docker restart categorizer-app"
echo ""
echo "Container'ı silmek için:"
echo "  docker rm -f categorizer-app"
echo "==========================================" 