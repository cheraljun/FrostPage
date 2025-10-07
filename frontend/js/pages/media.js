/**
 * 媒体页面
 */
import { ContentPageBase } from '../core/ContentPageBase.js';
import { USER_PAGE_CONFIGS } from '../config/pageConfigs.js';

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    new ContentPageBase(USER_PAGE_CONFIGS.media);
});

export default ContentPageBase;

