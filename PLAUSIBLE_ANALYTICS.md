# VIN Stressors - Plausible Analytics Integration

## 🔍 Privacy-Focused Analytics Setup

The VIN Stressors platform now includes **Plausible Analytics** for privacy-focused visitor tracking and user behavior analysis.

### ✅ What's Tracked

#### **Page Views**
- Automatic page view tracking
- No cookies or personal data collection
- Privacy-compliant analytics

#### **Custom Events**
| Event | Description | Properties |
|-------|-------------|------------|
| `Platform Loaded` | Initial platform load | `leads_count`, `total_revenue` |
| `Tab Switch` | User switches between tabs | `tab` (intelligence/engagement/analytics) |
| `Leads Sorted` | User sorts lead database | `sort_type` (urgency/timestamp/revenue) |
| `Lead Selected` | User selects a lead for details | `customer`, `status`, `risk_score`, `revenue` |
| `Channel Switch` | User switches communication channel | `channel` (sms/email/phone), `customer`, `status` |
| `AI Messages Generated` | Successful AI message generation | `customer`, `channel`, `personalized`, `message_count` |
| `AI Fallback Used` | AI fails, fallback messages used | `customer`, `channel`, `error` |

### 🔧 Configuration

#### **Environment Variables**
```bash
# Set your domain for Plausible tracking
PLAUSIBLE_DOMAIN=yomuffler.onrender.com

# For custom domains, update accordingly:
PLAUSIBLE_DOMAIN=yourdomain.com
```

#### **Default Behavior**
- If `PLAUSIBLE_DOMAIN` is not set, defaults to `yomuffler.onrender.com`
- Script loads asynchronously and won't block page rendering
- Works automatically on deployment to Render

### 📊 Analytics Dashboard

#### **Accessing Your Analytics**
1. Go to [plausible.io](https://plausible.io)
2. Create account and add your domain
3. View real-time analytics and insights

#### **Key Metrics to Monitor**
- **Page Views**: Overall platform usage
- **Tab Engagement**: Which sections users spend time in
- **Lead Interactions**: How users engage with customer data
- **AI Usage**: Success rate of AI message generation
- **Channel Preferences**: Which communication channels are popular

### 🎯 Business Intelligence

#### **User Journey Analysis**
```
Platform Load → Tab Navigation → Lead Selection → Channel Choice → AI Generation
```

#### **Conversion Tracking**
- **Lead Engagement Rate**: % of users who select leads
- **AI Usage Rate**: % of successful AI message generation
- **Channel Distribution**: SMS vs Email vs Phone preferences
- **High-Value Lead Focus**: Revenue-weighted engagement patterns

### 🔒 Privacy & Compliance

#### **Privacy-First Approach**
- ✅ **No cookies** - Cookieless tracking
- ✅ **No personal data** - No IP tracking
- ✅ **GDPR compliant** - Privacy by design
- ✅ **Lightweight** - 1KB script size
- ✅ **No data selling** - Your data stays yours

#### **Data Retention**
- Analytics data retained for 2 years
- No cross-site tracking
- No behavioral profiling
- Simple visitor counts and event tracking

### 🚀 Advanced Tracking

#### **Revenue Analytics**
```javascript
// Example: Track high-value lead interactions
window.plausible('High Value Lead', {
    props: {
        revenue: 465,
        status: 'CRITICAL',
        location: 'Tampa, FL'
    }
});
```

#### **A/B Testing Ready**
```javascript
// Example: Track interface variations
window.plausible('Design Test', {
    props: {
        variant: 'clean_professional',
        conversion: true
    }
});
```

### 📈 Success Metrics

#### **Platform Health**
- Daily active users
- Session duration
- Feature adoption rates
- Error rates (AI fallbacks)

#### **Business Impact**
- Lead engagement conversion
- Revenue opportunity tracking
- Geographic usage patterns
- Feature usage analytics

---

**Result**: Complete visibility into platform usage with privacy-first analytics that respect user privacy while providing actionable business insights. 