<script lang="ts">
	export let user_name: string;
	export let business_name: string;
	export let company_name = "Wagtee";
	export let dashboard_link: string;
</script>

<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #ffffff;">
	<!-- Header -->
	<div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 40px 30px; text-align: center;">
		<h1 style="color: #ffffff; font-size: 28px; font-weight: bold; margin: 0; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">
			{company_name}
		</h1>
		<p style="color: #e8f8ff; font-size: 16px; margin: 10px 0 0 0; opacity: 0.9;">
			منصة الحجوزات الذكية
		</p>
	</div>

	<!-- Content -->
	<div style="padding: 40px 30px; background-color: #ffffff;">
		<!-- Welcome Icon -->
		<div style="text-align: center; margin-bottom: 30px;">
			<div style="width: 80px; height: 80px; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); border-radius: 50%; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center;">
				<svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
					<path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
				</svg>
			</div>
			<h2 style="color: #2d3748; font-size: 28px; font-weight: bold; margin: 0 0 10px 0;">
				أهلاً وسهلاً {user_name}! 🎉
			</h2>
			<p style="color: #718096; font-size: 18px; margin: 0; line-height: 1.6;">
				نرحب بك في <strong>Wagtee</strong> - منصة الحجوزات الذكية التي ستغير طريقة إدارة أعمالك
			</p>
		</div>

		<!-- Business Welcome -->
		<div style="background: linear-gradient(135deg, #f8faff 0%, #e8f4f8 100%); border-radius: 12px; padding: 25px; margin: 30px 0; text-align: center;">
			<h3 style="color: #2d3748; font-size: 20px; margin: 0 0 15px 0;">
				تم تفعيل حساب <strong>{business_name}</strong> بنجاح ✅
			</h3>
			<p style="color: #4a5568; font-size: 16px; margin: 0; line-height: 1.6;">
				يمكنك الآن البدء في استخدام جميع ميزات المنصة لإدارة حجوزاتك بكفاءة
			</p>
		</div>

		<!-- Features Section -->
		<div style="margin: 40px 0;">
			<h3 style="color: #2d3748; font-size: 20px; margin: 0 0 20px 0; text-align: center;">
				ما يمكنك فعله الآن:
			</h3>
			
			<div style="display: grid; gap: 15px;">
				<!-- Feature 1 -->
				<div style="display: flex; align-items: center; padding: 15px; background-color: #f8f9fa; border-radius: 8px;">
					<div style="width: 40px; height: 40px; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-left: 15px;">
						<span style="color: white; font-size: 18px;">📅</span>
					</div>
					<div>
						<h4 style="color: #2d3748; font-size: 16px; margin: 0 0 5px 0;">إدارة الحجوزات</h4>
						<p style="color: #718096; font-size: 14px; margin: 0;">تتبع وإدارة جميع حجوزاتك في مكان واحد</p>
					</div>
				</div>

				<!-- Feature 2 -->
				<div style="display: flex; align-items: center; padding: 15px; background-color: #f8f9fa; border-radius: 8px;">
					<div style="width: 40px; height: 40px; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-left: 15px;">
						<span style="color: white; font-size: 18px;">💼</span>
					</div>
					<div>
						<h4 style="color: #2d3748; font-size: 16px; margin: 0 0 5px 0;">إدارة الخدمات</h4>
						<p style="color: #718096; font-size: 14px; margin: 0;">أضف وعدّل خدماتك وأسعارها بسهولة</p>
					</div>
				</div>

				<!-- Feature 3 -->
				<div style="display: flex; align-items: center; padding: 15px; background-color: #f8f9fa; border-radius: 8px;">
					<div style="width: 40px; height: 40px; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-left: 15px;">
						<span style="color: white; font-size: 18px;">📊</span>
					</div>
					<div>
						<h4 style="color: #2d3748; font-size: 16px; margin: 0 0 5px 0;">تقارير الأداء</h4>
						<p style="color: #718096; font-size: 14px; margin: 0;">اطلع على إحصائيات مفصلة عن أداء أعمالك</p>
					</div>
				</div>

				<!-- Feature 4 -->
				<div style="display: flex; align-items: center; padding: 15px; background-color: #f8f9fa; border-radius: 8px;">
					<div style="width: 40px; height: 40px; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-left: 15px;">
						<span style="color: white; font-size: 18px;">🔔</span>
					</div>
					<div>
						<h4 style="color: #2d3748; font-size: 16px; margin: 0 0 5px 0;">إشعارات WhatsApp</h4>
						<p style="color: #718096; font-size: 14px; margin: 0;">إشعارات تلقائية للعملاء عبر واتساب</p>
					</div>
				</div>
			</div>
		</div>

		<!-- CTA Button -->
		<div style="text-align: center; margin: 40px 0;">
			<a href="{dashboard_link}" 
			   style="display: inline-block; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: #ffffff; text-decoration: none; padding: 16px 32px; border-radius: 50px; font-size: 16px; font-weight: bold; box-shadow: 0 4px 15px rgba(79, 172, 254, 0.4); transition: all 0.3s ease;">
				ابدأ الآن - لوحة التحكم
			</a>
		</div>

		<!-- Next Steps -->
		<div style="background-color: #f8f9fa; border-radius: 8px; padding: 25px; margin: 30px 0;">
			<h3 style="color: #2d3748; font-size: 18px; margin: 0 0 15px 0;">الخطوات التالية:</h3>
			<ol style="color: #4a5568; font-size: 14px; line-height: 1.8; margin: 0; padding-right: 20px;">
				<li>أضف خدماتك الأولى في قسم "الخدمات"</li>
				<li>احضر ساعات العمل الخاصة بك</li>
				<li>شارك رابط الحجز مع عملائك</li>
				<li>ابدأ في استقبال الحجوزات!</li>
			</ol>
		</div>

		<!-- Support Section -->
		<div style="text-align: center; margin: 30px 0; padding: 20px; background-color: #fff8e1; border-radius: 8px; border: 1px solid #ffecb3;">
			<h3 style="color: #ef6c00; font-size: 16px; margin: 0 0 10px 0;">💡 نصيحة للبداية</h3>
			<p style="color: #bf360c; font-size: 14px; margin: 0; line-height: 1.6;">
				ابدأ بإضافة خدمة واحدة وجرب النظام، ثم أضف المزيد تدريجياً. 
				فريقنا متاح للمساعدة في أي وقت!
			</p>
		</div>
	</div>

	<!-- Footer -->
	<div style="background-color: #f7fafc; padding: 30px; text-align: center; border-top: 1px solid #e2e8f0;">
		<p style="color: #718096; font-size: 14px; margin: 0 0 15px 0;">
			هل تحتاج مساعدة في البداية؟ تواصل معنا:
		</p>
		
		<div style="margin: 20px 0;">
			<a href="mailto:support@wagtee.com" style="color: #4facfe; text-decoration: none; font-weight: bold; margin: 0 15px;">
				📧 support@wagtee.com
			</a>
			<a href="tel:+966xxxxxxxxx" style="color: #4facfe; text-decoration: none; font-weight: bold; margin: 0 15px;">
				📞 +966 XX XXX XXXX
			</a>
		</div>

		<div style="margin: 20px 0;">
			<a href="#" style="display: inline-block; margin: 0 10px; text-decoration: none;">
				<img src="https://via.placeholder.com/24x24/4facfe/ffffff?text=T" alt="Twitter" style="width: 24px; height: 24px; border-radius: 50%;">
			</a>
			<a href="#" style="display: inline-block; margin: 0 10px; text-decoration: none;">
				<img src="https://via.placeholder.com/24x24/4facfe/ffffff?text=F" alt="Facebook" style="width: 24px; height: 24px; border-radius: 50%;">
			</a>
			<a href="#" style="display: inline-block; margin: 0 10px; text-decoration: none;">
				<img src="https://via.placeholder.com/24x24/4facfe/ffffff?text=I" alt="Instagram" style="width: 24px; height: 24px; border-radius: 50%;">
			</a>
		</div>

		<div style="border-top: 1px solid #e2e8f0; padding-top: 20px; margin-top: 20px;">
			<p style="color: #a0aec0; font-size: 12px; margin: 0; direction: rtl;">
				© 2025 Wagtee. جميع الحقوق محفوظة.<br>
				الرياض، المملكة العربية السعودية
			</p>
		</div>
	</div>
</div>