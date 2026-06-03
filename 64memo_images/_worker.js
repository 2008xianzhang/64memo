// 访问 /random 时随机 302 跳转到一张 64memo 存档图片。
const IMAGES = [
  'album/3/wpId1474.jpg',
  'album/3/wpId1489.jpg',
  'album/4/wpId8809.jpg',
  'album/4/wpId8710.jpg',
  'album/4/wpId8803.jpg',
  'album/5/0926.jpg',
  'album/5/5232.jpg',
  'album/5/6763.jpg',
  'album/6/wpId1612.jpg',
  'album/7/C074a.jpg',
  'album/7/C075a.jpg',
  'album/7/A057a.jpg',
  'album/7/A051+-.jpg',
  'album/7/Z134.jpg',
  'album/7/Z040a.jpg',
  'album/7/Z152.jpg',
  'album/7/Z060.jpg',
  'album/9/P004-5.jpg',
  'album/9/P105a.JPG',
  'album/9/P105b.jpg',
  'album/9/P109b.JPG',
  'album/9/P114a.JPG',
  'album/10/A030-1.jpg',
  'album/10/A087.JPG',
  'album/10/A058-9a.jpg',
  'album/10/A088a.JPG',
  'album/10/A037a.jpg',
  'album/10/A018.JPG',
  'album/10/A025a.JPG',
  'album/10/A086-7.jpg',
  'album/12/BJ056a.JPG',
  'album/12/BJ125c.JPG',
  'album/12/BJ061a.JPG',
  'album/12/BJ062-3.jpg',
  'album/12/BJ064b.JPG',
  'album/12/BJ090a.JPG',
  'album/12/BJ069c.JPG',
  'album/12/BJ077.JPG',
  'album/12/BJ140-1a.jpg',
  'album/12/BJ140-1.JPG',
  'images/760/094.jpg',
  'images/760/103.jpg',
  'images/760/Bike.jpg',
  'images/760/020.jpg',
  'images/760/RMRBao.jpg',
  'pub/uploads/wpId12076.jpg',
  'pub/uploads/wpId16250.jpg',
  'pub/uploads/wpId1404.jpg',
  'pub/uploads/wpId1406.jpg',
  'pub/uploads/wpId1408.jpg',
  'pub/uploads/wpId1424.jpg',
  'pub/uploads/wpId13233.jpg',
  'pub/uploads/wpId1432.jpg',
  'pub/uploads/wpId14402.jpg',
  'pub/uploads/wpId1442.jpg',
  'pub/uploads/wpId14449.jpg',
  'pub/uploads/wpId13483.jpg',
  'pub/uploads/wpId1454.jpg',
  'pub/uploads/wpId1455.jpg',
  'pub/uploads/wpId9093.jpg',
  'pub/uploads/wpId1456.jpg',
  'pub/uploads/wpId1457.jpg',
  'pub/uploads/wpId13519.jpg',
  'pub/uploads/wpId13524.jpg',
  'pub/uploads/wpId13525.jpg',
  'pub/uploads/wpId13528.jpg',
  'pub/uploads/wpId18830.jpg',
  'pub/uploads/wpId2030.jpg',
  'pub/uploads/wpId1498.jpg',
  'pub/uploads/wpId2305.jpg',
  'pub/uploads/wpId2437.jpg',
  'pub/uploads/wpId9688.jpg',
  'pub/uploads/wpId13773.jpg',
];

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname !== '/random' && url.pathname !== '/random/') {
      return env.ASSETS.fetch(request);
    }

    const pick = IMAGES[Math.floor(Math.random() * IMAGES.length)];
    // 逐段编码，保留 "/" 分隔符；避免 "+"、空格等被误解析。
    const encoded = pick.split('/').map(encodeURIComponent).join('/');
    const target = new URL('/' + encoded, url.origin);
    return Response.redirect(target.toString(), 302);
  },
};
