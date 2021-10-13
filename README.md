# yzb_download
Download Video from Yizhibo.com

需要配合ffmpeg使用,自己下载ffmpeg.exe并在配置文件中填写具体的路径


{
  "hwaccel": "cuvid",    // ffmpeg 使用GPU加速 支持参数 "cuda","dxva2","qsv","d3d11va","cuvid"等  
  "decoder": "h264_cuvid", // 解码 "h264","h264_qsv","h264_cuvid","hevc","hevc_qsv","hevc_cuvid" 等
  "encoder": "h264_nvenc", // 编码 "libx264","libx264rgb","h264_amf","h264_nvenc","h264_qsv","nvenc","nvenc_h264","libx265","nvenc_hevc","hevc_amf","hevc_nvenc","hevc_qsv" 等
  "device": "0",           //  0 = 首选GPU  , 1 = 第二个GPU
  "CORP_ID": "****",       // 企业微信ID 用于发送通知到你的微信, 自己搜索具体使用
  "CORP_SECRET": "****",   // 密钥
  "AgentId": "****",       // 应用ID
  "video_path": "Stock\\Video", // 视频保存目录
  "audio_path": "Stock\\Audio", //  提取音频保存路径
  "ffmpeg_path": "ffmpeg.exe",  // ffmpeg路径
  "log_path": "log",    // 日志路径
  "start_hour": 0,    // 每天自动检查新视频的时 h
  "end_hour": 22,     // 每天结束检查新视频的时 h
  "user_id": ******,  // 一直播主播的id
  "yzb_url": "http://www.yizhibo.com/member/personel/user_videos?memberid=",
  "tt0": 8    // 检查新视频的时间间隔 秒
}
