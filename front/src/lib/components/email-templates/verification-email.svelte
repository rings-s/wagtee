<script lang="ts">
	export let verification_code: string;
	export let user_name: string;
	export let company_name = "Wagtee";
</script>

<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #ffffff;">
	<!-- Header -->
	<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center;">
		<h1 style="color: #ffffff; font-size: 28px; font-weight: bold; margin: 0; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">
			{company_name}
		</h1>
		<p style="color: #e8f4f8; font-size: 16px; margin: 10px 0 0 0; opacity: 0.9;">
			منصة الحجوزات الذكية
		</p>
	</div>

	<!-- Content -->
	<div style="padding: 40px 30px; background-color: #ffffff;">
		<!-- Welcome Message -->
		<div style="text-align: center; margin-bottom: 30px;">
			<div style="width: 80px; height: 80px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 50%; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center;">
				<svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
					<path d="M20 6L9 17L4 12" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
				</svg>
			</div>
			<h2 style="color: #2d3748; font-size: 24px; font-weight: bold; margin: 0 0 10px 0;">
				مرحباً {user_name}!
			</h2>
			<p style="color: #718096; font-size: 16px; margin: 0; line-height: 1.6;">
				نحن سعداء بانضمامك إلى منصة Wagtee. يرجى التحقق من بريدك الإلكتروني لإكمال التسجيل.
			</p>
		</div>

		<!-- Verification Code -->
		<div style="background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%); border: 2px dashed #cbd5e0; border-radius: 12px; padding: 30px; text-align: center; margin: 30px 0;">
			<p style="color: #4a5568; font-size: 14px; margin: 0 0 15px 0; text-transform: uppercase; letter-spacing: 1px;">
				رمز التحقق
			</p>
			<div style="background: #ffffff; border: 2px solid #667eea; border-radius: 8px; padding: 20px; display: inline-block; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);">
				<span style="font-family: 'Courier New', monospace; font-size: 32px; font-weight: bold; color: #667eea; letter-spacing: 8px;">
					{verification_code}
				</span>
			</div>
			<p style="color: #718096; font-size: 12px; margin: 15px 0 0 0;">
				صالح لمدة 15 دقيقة فقط
			</p>
		</div>

		<!-- Instructions -->
		<div style="background-color: #f8f9fa; border-radius: 8px; padding: 20px; margin: 30px 0;">
			<h3 style="color: #2d3748; font-size: 18px; margin: 0 0 15px 0;">كيفية التحقق:</h3>
			<ol style="color: #4a5568; font-size: 14px; line-height: 1.8; margin: 0; padding-right: 20px;">
				<li>انسخ رمز التحقق أعلاه</li>
				<li>ارجع إلى صفحة التسجيل في Wagtee</li>
				<li>ألصق الرمز في الحقل المخصص</li>
				<li>اضغط على "تأكيد التحقق"</li>
			</ol>
		</div>

		<!-- Security Notice -->
		<div style="background-color: #fff5f5; border: 1px solid #fed7d7; border-radius: 6px; padding: 15px; margin: 20px 0;">
			<p style="color: #c53030; font-size: 13px; margin: 0; line-height: 1.5;">
				🔒 <strong>ملاحظة أمنية:</strong> لا تشارك هذا الرمز مع أي شخص. فريق Wagtee لن يطلب منك هذا الرمز عبر الهاتف أو البريد الإلكتروني.
			</p>
		</div>
	</div>

	<!-- Footer -->
	<div style="background-color: #f7fafc; padding: 30px; text-align: center; border-top: 1px solid #e2e8f0;">
		<p style="color: #718096; font-size: 14px; margin: 0 0 10px 0;">
			هل تحتاج مساعدة؟ <a href="mailto:support@wagtee.com" style="color: #667eea; text-decoration: none;">تواصل معنا</a>
		</p>
		
		<div style="margin: 20px 0;">
			<a href="#" style="display: inline-block; margin: 0 10px; text-decoration: none;">
				<img src="https://via.placeholder.com/24x24/667eea/ffffff?text=T" alt="Twitter" style="width: 24px; height: 24px; border-radius: 50%;">
			</a>
			<a href="#" style="display: inline-block; margin: 0 10px; text-decoration: none;">
				<img src="https://via.placeholder.com/24x24/667eea/ffffff?text=F" alt="Facebook" style="width: 24px; height: 24px; border-radius: 50%;">
			</a>
			<a href="#" style="display: inline-block; margin: 0 10px; text-decoration: none;">
				<img src="https://via.placeholder.com/24x24/667eea/ffffff?text=I" alt="Instagram" style="width: 24px; height: 24px; border-radius: 50%;">
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